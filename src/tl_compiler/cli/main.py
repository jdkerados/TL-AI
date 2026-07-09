"""tl-ai CLI: validate and compile the specification corpus."""

import argparse
from collections.abc import Sequence
from pathlib import Path

from tl_compiler import COMPILER_VERSION
from tl_compiler.config import DEFAULT_BUILD_DIR, DEFAULT_SCHEMAS_DIR, DEFAULT_SPECS_DIR
from tl_compiler.generators import generate_artifacts
from tl_compiler.ir import build_ir
from tl_compiler.pipeline import run_validation
from tl_compiler.validator import ValidationReport


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tl-ai", description="TL-AI specification compiler")
    parser.add_argument("--version", action="version", version=f"tl-ai {COMPILER_VERSION}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--specs",
        type=Path,
        default=Path(DEFAULT_SPECS_DIR),
        help="specifications directory (default: specifications/)",
    )
    common.add_argument(
        "--schemas",
        type=Path,
        default=Path(DEFAULT_SCHEMAS_DIR),
        help="JSON Schemas directory (default: schemas/)",
    )

    validate = subparsers.add_parser(
        "validate", parents=[common], help="validate every specification file"
    )
    validate.add_argument(
        "--report",
        type=Path,
        default=Path(DEFAULT_BUILD_DIR) / "validation_report.json",
        help="validation report output path (default: build/validation_report.json)",
    )

    compile_cmd = subparsers.add_parser(
        "compile", parents=[common], help="compile specifications into IR and build manifest"
    )
    compile_cmd.add_argument(
        "--output",
        type=Path,
        default=Path(DEFAULT_BUILD_DIR),
        help="build output directory (default: build/)",
    )
    return parser


def _print_summary(report: ValidationReport) -> None:
    for issue in report.issues:
        print(f"{issue.severity.value.upper()} [{issue.code}] {issue.file}: {issue.message}")
    print(
        f"Scanned {report.files_scanned} file(s): "
        f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
    )


def _cmd_validate(specs_dir: Path, schemas_dir: Path, report_path: Path) -> int:
    _, report = run_validation(specs_dir, schemas_dir)
    report.write(report_path)
    _print_summary(report)
    print(f"Validation report written to {report_path}")
    return 0 if report.is_valid else 1


def _cmd_compile(specs_dir: Path, schemas_dir: Path, output_dir: Path) -> int:
    specs, report = run_validation(specs_dir, schemas_dir)
    _print_summary(report)
    if not report.is_valid:
        print("Compilation aborted: validation failed.")
        return 1
    ir = build_ir(specs)
    ir_path, manifest_path = generate_artifacts(ir, specs_dir, output_dir)
    print(f"Compiled {len(ir.entities)} entity(ies).")
    print(f"IR written to {ir_path}")
    print(f"Build manifest written to {manifest_path}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Entry point. Returns the process exit code."""
    args = _build_parser().parse_args(argv)
    if args.command == "validate":
        return _cmd_validate(args.specs, args.schemas, args.report)
    return _cmd_compile(args.specs, args.schemas, args.output)


def run() -> None:
    """Console-script wrapper."""
    raise SystemExit(main())
