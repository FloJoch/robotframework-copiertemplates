"""Many answer combinations must result in runnable projects.

Checked: every option alone (with each library variant), everything selected in all variants and 40 random
but fixed combinations. All 2^10 combinations would be too many; the options are independent of each other
(own files per library), so this selection is enough.

The full project is set up once for real (uv sync, Chromium, npm); its environment additionally gets the
libraries of the other variants. For every combination the following run: robotcode -p check robot,
robocop check and robotcode robot (profile dev, needs internet).
Takes about 20 minutes: uv run pytest -m matrix
"""
import os
import random
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
from copier import run_copy

TEMPLATE_ROOT = Path(__file__).resolve().parent.parent
OPTIONS = ["include_web", "include_api", "include_database", "include_desktop", "include_mobile",
            "include_faker", "include_email", "include_doctest", "include_sap", "include_accessibility"]
VARIANTS = [
    {"web_library": "browser", "api_library": "requests", "database_driver": "sqlite"},
    {"web_library": "selenium", "api_library": "restinstance", "database_driver": "postgresql"},
    {"web_library": "browser", "api_library": "restinstance", "database_driver": "mysql"},
    {"web_library": "selenium", "api_library": "requests", "database_driver": "sqlite"},
]
SCRIPTS = "Scripts" if sys.platform == "win32" else "bin"
SUFFIX = ".exe" if sys.platform == "win32" else ""


def combinations():
    all_no = dict.fromkeys(OPTIONS, False)
    cases = []
    for option in OPTIONS:
        for variant in VARIANTS[:2]:
            cases.append({**all_no, option: True, **variant})
    for variant in VARIANTS:
        cases.append({**dict.fromkeys(OPTIONS, True), **variant})
    rng = random.Random(42)
    for number in range(40):
        selection = {option: rng.random() < 0.5 for option in OPTIONS}
        cases.append({**selection, **VARIANTS[number % len(VARIANTS)]})
    return cases


@pytest.fixture(scope="module")
def full_project():
    with tempfile.TemporaryDirectory(prefix="rf", ignore_cleanup_errors=True) as folder:
        target = Path(folder) / "voll"
        run_copy(str(TEMPLATE_ROOT), str(target), vcs_ref="HEAD", data={"project_name": "Voll", **dict.fromkeys(OPTIONS, True)},
                 defaults=True, unsafe=True)
        python = str(target / ".venv" / SCRIPTS / ("python" + SUFFIX))
        subprocess.run(["uv", "pip", "install", "--python", python, "robotframework-seleniumlibrary", "RESTinstance",
                        "psycopg2-binary", "pymysql"], check=True)
        yield target


@pytest.mark.matrix
def test_many_combinations_run(full_project):
    scripts = full_project / ".venv" / SCRIPTS
    env = dict(os.environ, PATH=str(scripts) + os.pathsep + os.environ["PATH"], VIRTUAL_ENV=str(full_project / ".venv"))
    errors = []
    for case_data in combinations():
        with tempfile.TemporaryDirectory(prefix="sw", ignore_cleanup_errors=True) as folder:
            target = Path(folder)
            run_copy(str(TEMPLATE_ROOT), str(target), vcs_ref="HEAD", data={"project_name": "Matrix", **case_data},
                     defaults=True, overwrite=True, unsafe=True, skip_tasks=True, quiet=True)
            if case_data["include_accessibility"]:
                shutil.copytree(full_project / "node_modules", target / "node_modules")
            for name, cmd in [
                ("check", [str(scripts / f"robotcode{SUFFIX}"), "-p", "check", "robot"]),
                ("robocop", [str(scripts / f"robocop{SUFFIX}"), "check"]),
                ("run", [str(scripts / f"robotcode{SUFFIX}"), "robot"]),
            ]:
                r = subprocess.run(cmd, cwd=target, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
                if r.returncode != 0:
                    selected = [o.removeprefix("include_") for o in OPTIONS if case_data[o]]
                    errors.append(f"{'+'.join(selected) or 'nothing'} {case_data['web_library']}/{case_data['api_library']}"
                                  f"/{case_data['database_driver']} [{name}]: {(r.stdout + r.stderr)[-500:]}")
                    break
    assert not errors, "\n".join(errors)
