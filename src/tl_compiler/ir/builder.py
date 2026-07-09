"""IR builder: transforms validated specification files into the IR."""

from tl_compiler.ir.model import BuildIR, IREntity
from tl_compiler.parser import SpecFile
from tl_compiler.resolver import collect_references


def build_ir(specs: list[SpecFile]) -> BuildIR:
    """Build the IR from loaded specification files (skips unparsable/uncategorized files)."""
    entities: list[IREntity] = []
    for spec in specs:
        if spec.data is None or spec.category is None:
            continue
        metadata = spec.data.get("metadata", {})
        status = metadata.get("status", "") if isinstance(metadata, dict) else ""
        entities.append(
            IREntity(
                stable_id=str(spec.data.get("id", "")),
                entity_type=str(spec.data.get("type", "")),
                name=str(spec.data.get("name", "")),
                version=str(spec.data.get("version", "")),
                patch=str(spec.data.get("patch", "")),
                status=str(status),
                source_path=spec.relative_path,
                references=collect_references(spec.data),
                payload=spec.data,
            )
        )
    entities.sort(key=lambda entity: entity.stable_id)
    return BuildIR(entities=tuple(entities))
