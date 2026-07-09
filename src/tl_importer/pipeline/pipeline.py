"""ImportPipeline: interface-driven orchestration of the import stages.

Source -> Parser -> Normalizer -> Validator -> Compiler -> Database

The pipeline only wires interfaces together; every stage is injected.
"""

from dataclasses import dataclass
from datetime import UTC, datetime

from tl_importer.importers import EntityImporter
from tl_importer.models import (
    ImportContext,
    ImportResult,
    ImportStatus,
    NormalizedEntity,
)
from tl_importer.normalizers import Normalizer
from tl_importer.parsers import Parser
from tl_importer.providers import Provider
from tl_importer.validators import ImportValidator


@dataclass(frozen=True)
class ImportPipeline:
    """Orchestrates one import run over injected stage implementations."""

    provider: Provider
    parser: Parser
    normalizer: Normalizer
    validator: ImportValidator
    importer: EntityImporter

    def run(self, context: ImportContext) -> ImportResult:
        """Execute the pipeline for the job in the given context."""
        result = ImportResult(job_id=context.job.job_id)
        valid: list[NormalizedEntity] = []

        for document in self.provider.fetch(context):
            result.documents_fetched += 1
            if not self.parser.can_parse(document):
                result.errors.append(f"no parser for document: {document.uri}")
                continue
            for raw in self.parser.parse(document, context):
                result.raw_entities += 1
                normalized = self.normalizer.normalize(raw, context)
                result.normalized_entities += 1
                report = self.validator.validate(normalized, context)
                result.reports.append(report)
                if report.is_valid:
                    valid.append(normalized)

        result.valid_entities = len(valid)
        if valid and not context.dry_run:
            result.imported_entities = self.importer.persist(valid, context)

        invalid = result.normalized_entities - result.valid_entities
        if result.normalized_entities > 0 and result.valid_entities == 0:
            result.status = ImportStatus.FAILED
        elif invalid > 0 or result.errors:
            result.status = ImportStatus.PARTIAL
        else:
            result.status = ImportStatus.SUCCESS
        result.finished_at = datetime.now(UTC)
        return result
