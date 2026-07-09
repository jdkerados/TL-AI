"""Build manifest and IR artifact generator."""

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from tl_compiler import COMPILER_VERSION
from tl_compiler.ir import BuildIR


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generate_artifacts(ir: BuildIR, specs_dir: Path, output_dir: Path) -> tuple[Path, Path]:
    """Write ir.json and build_manifest.json to output_dir. Returns their paths."""
    output_dir.mkdir(parents=True, exist_ok=True)

    ir_path = output_dir / "ir.json"
    ir_path.write_text(json.dumps(ir.to_dict(), indent=2) + "\n", encoding="utf-8")

    entity_counts = Counter(entity.entity_type for entity in ir.entities)
    manifest: dict[str, Any] = {
        "compilerVersion": COMPILER_VERSION,
        "generatedAt": datetime.now(UTC).isoformat(),
        "specificationsDir": str(specs_dir),
        "entityCount": len(ir.entities),
        "entityCounts": dict(sorted(entity_counts.items())),
        "artifacts": {"ir": ir_path.name},
        "entities": [
            {
                "stableId": entity.stable_id,
                "type": entity.entity_type,
                "name": entity.name,
                "version": entity.version,
                "patch": entity.patch,
                "status": entity.status,
                "sourcePath": entity.source_path,
                "sha256": _sha256(specs_dir / entity.source_path),
                "references": list(entity.references),
            }
            for entity in ir.entities
        ],
    }
    manifest_path = output_dir / "build_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return ir_path, manifest_path
