"""Compares the versions used by the template with the latest releases on PyPI.

Robot Framework is pinned in copier.yml (rf_version) on master; older versions live on rf-<version>
branches. Nothing is changed automatically - the report only informs. All other libraries in the generated
projects are not pinned; they are listed so that new major versions can be tested early.
Writes GitHub step outputs to stdout and a report to update-report.md.
"""

import json
import re
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PYPROJECT = ROOT / "template" / "pyproject.toml.jinja"


def pypi(package: str, version: str = "") -> dict:
    url = f"https://pypi.org/pypi/{package}/{version + '/' if version else ''}json"
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)["info"]


def latest(package: str) -> str:
    return pypi(package)["version"]


def newest_python(classifiers: list[str]) -> str:
    """Highest Python 3.x version listed in the classifiers of a package."""
    versions = [c.rsplit("::", 1)[1].strip() for c in classifiers if re.fullmatch(r"Programming Language :: Python :: 3\.\d+", c)]
    return max(versions, key=lambda v: tuple(map(int, v.split("."))))


def main() -> None:
    copier_yml = (ROOT / "copier.yml").read_text(encoding="utf-8")
    pinned = re.search(r'^rf_version:\n(?:  .*\n)*?  default: "([^"]+)"', copier_yml, flags=re.M).group(1)
    python = re.search(r'^python_version:\n(?:  .*\n)*?  default: "([^"]+)"', copier_yml, flags=re.M).group(1)
    newest = latest("robotframework")
    python_supported = newest_python(pypi("robotframework", pinned)["classifiers"])

    libraries = sorted(set(re.findall(r'"([A-Za-z][A-Za-z0-9_.-]+)(?:\[[^\]]*\])?(?:[<>=!~][^"]*)?"',
                                      TEMPLATE_PYPROJECT.read_text(encoding="utf-8")))
                       - {"robotframework"})
    rows = []
    for name in libraries:
        try:
            rows.append(f"| `{name}` | {latest(name)} |")
        except Exception:  # noqa: BLE001 - not a PyPI package name (e.g. a Jinja fragment)
            continue

    rf_outdated = pinned != newest
    python_outdated = tuple(map(int, python_supported.split("."))) > tuple(map(int, python.split(".")))
    outdated = rf_outdated or python_outdated
    if rf_outdated:
        title = f"Robot Framework {newest} is available (template uses {pinned})"
    else:
        title = f"Robot Framework {pinned} supports Python {python_supported} (template uses {python})"
    report = [
        f"## {title}" if outdated else f"Robot Framework {pinned} and Python {python} are up to date.",
        "",
        f"- Robot Framework: template {pinned}, latest {newest}.",
        f"- Python: template {python}, Robot Framework {pinned} supports up to {python_supported}. Raise",
        "  `python_version` only after `uv run pytest -m slow` passes - libraries often support new Python",
        "  versions later than Robot Framework (e.g. PlatynUI is limited to Python < 3.14).",
        "",
        *([
            "Nothing has been changed. To offer the new version, follow docs/versions-and-updates.md, *Adding a new",
            f"Robot Framework version*: raise `rf_version` on `master`, run the tests, tag, and create the branch `rf-{newest}`.",
            f"Projects on {pinned} keep using the branch `rf-{pinned}`.",
            "",
        ] if rf_outdated else ["Nothing has been changed automatically.", ""]),
        "Latest versions of the other libraries (not pinned, resolved by uv in each project):",
        "",
        "| Package | Latest on PyPI |",
        "|---|---|",
        *rows,
    ]
    (ROOT / "update-report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    print(f"outdated={'true' if outdated else 'false'}")
    print(f"title={title}")


if __name__ == "__main__":
    main()
