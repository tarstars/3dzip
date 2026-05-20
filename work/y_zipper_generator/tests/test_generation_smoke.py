from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def run_cli(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "yzipper.cli", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_cli_help_works(project_root: Path) -> None:
    result = run_cli("--help", cwd=project_root)
    assert result.returncode == 0
    assert "--part" in result.stdout


def test_dry_run_writes_nothing(tmp_path: Path, project_root: Path) -> None:
    out = tmp_path / "dry"
    result = run_cli("--part", "all", "--dry-run", "--out", str(out), cwd=project_root)
    assert result.returncode == 0, result.stderr
    assert "Dry run complete" in result.stdout
    assert not out.exists()


def test_strip_generation_creates_file(tmp_path: Path, project_root: Path) -> None:
    out = tmp_path / "strip"
    result = run_cli("--part", "strip", "--teeth", "6", "--out", str(out), cwd=project_root)
    assert result.returncode == 0, result.stderr
    assert list(out.glob("strip_teeth6_*.stl"))


def test_slider_generation_creates_file(tmp_path: Path, project_root: Path) -> None:
    out = tmp_path / "slider"
    result = run_cli("--part", "slider", "--out", str(out), cwd=project_root)
    assert result.returncode == 0, result.stderr
    assert list(out.glob("slider_clearance*.stl"))


def test_coupon_generation_creates_files(tmp_path: Path, project_root: Path) -> None:
    out = tmp_path / "coupon"
    result = run_cli("--part", "coupon", "--teeth", "8", "--out", str(out), cwd=project_root)
    assert result.returncode == 0, result.stderr
    files = sorted(p.name for p in out.glob("*.stl"))
    assert any(name.startswith("coupon_strip") for name in files)
    assert any(name.startswith("coupon_slider") for name in files)
    assert any("preview" in name for name in files)


def test_reference_like_generation_creates_ladder_files(tmp_path: Path, project_root: Path) -> None:
    out = tmp_path / "reference"
    result = run_cli("--part", "all", "--preset", "reference-like", "--out", str(out), cwd=project_root)
    assert result.returncode == 0, result.stderr
    files = sorted(p.name for p in out.glob("*.stl"))
    assert any(name.startswith("strip_ladder") for name in files)
    assert any(name.startswith("strips3_ladder") for name in files)
    assert any(name.startswith("preview_ladder") for name in files)


def test_invalid_parameters_fail(project_root: Path) -> None:
    result = run_cli("--part", "strip", "--teeth", "0", cwd=project_root)
    assert result.returncode == 2
    assert "teeth" in result.stderr
