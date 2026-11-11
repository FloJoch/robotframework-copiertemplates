import re
import tempfile
from pathlib import Path

import pytest
from copier import run_copy

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent

JINJA_LEFTOVER = re.compile(r"{[{%]|[%}]}")
GITHUB_EXPRESSION = re.compile(r"\$\{\{[^}]*\}\}")  # ${{ ... }} in GitHub workflows is not Jinja


def render(dst_path: Path, **data) -> Path:
    """Render the template without the setup tasks (git init, uv sync, ...)."""
    data.setdefault("project_name", "Test Project")
    run_copy(
        str(TEMPLATE_ROOT),
        str(dst_path),
        vcs_ref="HEAD",  # working copy, not the latest tag
        data=data,
        defaults=True,
        overwrite=True,
        unsafe=True,
        skip_tasks=True,
    )
    return dst_path


def assert_no_jinja_leftovers(project_dir: Path) -> None:
    for path in project_dir.rglob("*"):
        if path.is_file() and path.name != ".copier-answers.yml" and path.suffix not in {".png", ".pdf"}:
            text = path.read_text(encoding="utf-8", errors="ignore")
            text = GITHUB_EXPRESSION.sub("", text)
            assert not JINJA_LEFTOVER.search(text), f"Jinja leftover in {path}"


def assert_no_forbidden_filename_chars(project_dir: Path) -> None:
    forbidden = set('<>:"|?*')
    for path in project_dir.rglob("*"):
        for part in path.relative_to(project_dir).parts:
            assert not (forbidden & set(part)), f"Forbidden character in: {part}"


@pytest.fixture
def render_project(tmp_path):
    def _render(**data):
        dst = tmp_path / "project"
        return render(dst, **data)

    return _render


@pytest.fixture
def short_path():
    """Short temp folder: Chromium fails on long paths on Windows (pytest tmp_path is too long)."""
    with tempfile.TemporaryDirectory(prefix="rf", ignore_cleanup_errors=True) as folder:
        yield Path(folder)
