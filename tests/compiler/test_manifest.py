"""Tests for the build manifest generator."""

import json
from pathlib import Path

from tl_compiler.generators import generate_artifacts
from tl_compiler.ir import build_ir
from tl_compiler.parser import load_specifications


def test_generates_ir_and_manifest(specs_dir: Path, tmp_path: Path) -> None:
    output_dir = tmp_path / "build"
    ir = build_ir(load_specifications(specs_dir))
    ir_path, manifest_path = generate_artifacts(ir, specs_dir, output_dir)
    assert ir_path.is_file()
    assert manifest_path.is_file()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["entityCount"] == 2
    assert manifest["entityCounts"] == {"Trait": 1, "Weapon": 1}
    assert manifest["artifacts"] == {"ir": "ir.json"}
    entities = {entry["stableId"]: entry for entry in manifest["entities"]}
    weapon = entities["tl.weapon.test_sword"]
    assert weapon["references"] == ["tl.trait.test_trait"]
    assert len(weapon["sha256"]) == 64

    ir_data = json.loads(ir_path.read_text(encoding="utf-8"))
    assert len(ir_data["entities"]) == 2
