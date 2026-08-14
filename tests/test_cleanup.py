import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "skills" / "clean-workspace-artifacts" / "scripts" / "clean_workspace.py"


def run_cleaner(root: Path, *options: str):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--json", *options],
        text=True, capture_output=True, check=True,
    )


def test_cleanup_is_dry_run_first_and_preserves_domain_artifacts(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='fixture'\n", encoding="utf-8")
    (tmp_path / "skills").mkdir()
    (tmp_path / ".pytest_cache").mkdir()
    (tmp_path / ".pytest_cache" / "cache").write_text("generated", encoding="utf-8")
    (tmp_path / "dist").mkdir()
    (tmp_path / "dist" / "package.whl").write_text("generated", encoding="utf-8")
    (tmp_path / "summaries").mkdir()
    summary = tmp_path / "summaries" / "20260805_project.md"
    summary.write_text("reviewed", encoding="utf-8")
    (tmp_path / "reviews").mkdir()
    review = tmp_path / "reviews" / "pending.json"
    review.write_text("{}", encoding="utf-8")
    slide_dir = tmp_path / "slides" / "20260814_example" / "assets" / "analysis_run"
    slide_dir.mkdir(parents=True)
    run_log = slide_dir / "run.log"
    run_log.write_text("analysis provenance", encoding="utf-8")
    tex_dir = tmp_path / "slides" / "20260814_example"
    (tex_dir / "weekly-update.tex").write_text("presentation source", encoding="utf-8")
    latex_log = tex_dir / "weekly-update.log"
    latex_log.write_text("generated", encoding="utf-8")

    preview = json.loads(run_cleaner(tmp_path).stdout)
    selected = {item["path"] for item in preview["candidates"]}
    assert ".pytest_cache" in selected
    assert "dist" not in selected
    assert "slides/20260814_example/weekly-update.log" in selected
    assert "slides/20260814_example/assets/analysis_run/run.log" not in selected
    assert (tmp_path / ".pytest_cache").exists()

    run_cleaner(tmp_path, "--include-build-output", "--apply")
    assert not (tmp_path / ".pytest_cache").exists()
    assert not (tmp_path / "dist").exists()
    assert summary.read_text(encoding="utf-8") == "reviewed"
    assert review.read_text(encoding="utf-8") == "{}"
    assert run_log.read_text(encoding="utf-8") == "analysis provenance"
