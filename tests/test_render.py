import re
import subprocess
from pathlib import Path

import pytest
import yaml
from copier import run_copy

from conftest import TEMPLATE_ROOT, assert_no_forbidden_filename_chars, assert_no_jinja_leftovers

# Areas and the files each of them creates (paths in the generated project)
BROWSER_LAYER = ["resources/abilities/browser_ability.resource", "resources/interactions/browser_interactions.resource"]
PAGES = ["resources/pages/login_page.resource", "resources/pages/main_page.resource",
          "resources/pages/cart_page.resource", "resources/pages/settings_page.resource"]
OPTIONS = {
    "include_web": [*BROWSER_LAYER, *PAGES, "resources/tasks/web_tasks.resource",
                    "resources/assertions/web_assertions.resource", "tests/web/login.robot", "tests/web/cart.robot"],
    "include_api": ["resources/abilities/api_ability.resource", "resources/interactions/api_interactions.resource",
                    "resources/tasks/api_tasks.resource", "resources/assertions/api_assertions.resource",
                    "tests/api/todos_and_posts.robot"],
    "include_database": ["resources/abilities/database_ability.resource", "resources/interactions/database_interactions.resource",
                         "resources/tasks/database_tasks.resource", "resources/assertions/database_assertions.resource",
                         "tests/database/customers.robot"],
    "include_desktop": ["resources/abilities/desktop_ability.resource", "resources/pages/calculator_page.py",
                        "resources/interactions/desktop_interactions.resource", "resources/tasks/desktop_tasks.resource",
                        "resources/assertions/desktop_assertions.resource", "tests/desktop/calculator.robot"],
    "include_mobile": ["resources/abilities/mobile_ability.resource", "resources/pages/android_settings_page.resource",
                       "resources/interactions/mobile_interactions.resource", "resources/tasks/mobile_tasks.resource",
                       "resources/assertions/mobile_assertions.resource", "tests/mobile/settings.robot"],
    "include_faker": ["resources/abilities/faker_ability.resource", "resources/interactions/faker_interactions.resource",
                      "resources/tasks/faker_tasks.resource", "resources/assertions/faker_assertions.resource",
                      "tests/testdata/generate_customers.robot"],
    "include_email": ["resources/abilities/email_ability.resource", "resources/interactions/email_interactions.resource",
                      "resources/tasks/email_tasks.resource", "resources/assertions/email_assertions.resource",
                      "tests/email/mailbox.robot"],
    "include_doctest": ["resources/abilities/doctest_ability.resource", "resources/interactions/doctest_interactions.resource",
                        "resources/tasks/doctest_tasks.resource", "resources/assertions/doctest_assertions.resource",
                        "tests/documents/image_and_pdf.robot", "data/reference/example.png", "data/reference/example.pdf"],
    "include_sap": ["resources/abilities/sap_ability.resource", "resources/interactions/sap_interactions.resource",
                    "resources/tasks/sap_tasks.resource", "resources/assertions/sap_assertions.resource",
                    "tests/sap/user_data.robot"],
    "include_accessibility": [*BROWSER_LAYER, *PAGES, "resources/interactions/accessibility_interactions.resource",
                              "resources/tasks/accessibility_tasks.resource",
                              "resources/assertions/accessibility_assertions.resource",
                              "tests/accessibility/without_login.robot", "tests/accessibility/with_login.robot",
                              "resources/axe_extension.js", "package.json"],
}
ALL_NO = {key: False for key in OPTIONS}
ALL_YES = {key: True for key in OPTIONS}
CORE = ["README.md", ".gitignore", ".python-version", "pyproject.toml", "robot.toml", ".vscode/extensions.json",
        ".vscode/settings.json", ".copier-answers.yml", "resources/main.resource", "data/keys/.gitkeep",
        "resources/interactions/core_interactions.resource", "resources/tasks/core_tasks.resource",
        "resources/assertions/core_assertions.resource", "tests/core/credentials.robot",
        ".agents/skills/robot-project/SKILL.md", ".agents/skills/robot-write-test/SKILL.md",
        ".agents/skills/robot-explain-results/SKILL.md"]
AREAS = {"web": "include_web", "api": "include_api", "email": "include_email", "database": "include_database",
         "faker": "include_faker", "doctest": "include_doctest", "accessibility": "include_accessibility",
         "desktop": "include_desktop", "mobile": "include_mobile", "sap": "include_sap"}
BASIC = ["web", "api"]
# Only areas with a real choice ask for the library
LIBRARY_QUESTIONS = {"web_library": ("web", {"browser", "selenium"}), "api_library": ("api", {"requests", "restinstance"}),
                     "database_driver": ("database", {"sqlite", "postgresql", "mysql"})}
RF_VERSION = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))["rf_version"]["default"]


def read(project, rel_path):
    return (project / rel_path).read_text(encoding="utf-8")


# ----------------------------------------------------------------------------- Dialog
def test_dialog_is_one_list_and_asks_libraries_only_where_there_is_a_choice():
    questions = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))
    assert questions["language"]["choices"] == {"Deutsch": "de", "English": "en"}
    areas = questions["test_areas"]
    assert areas["multiselect"] is True and areas["default"] == ["web"]
    assert list(areas["choices"].values()) == list(AREAS)
    assert "language == 'en'" in areas["help"] and "Enter" in areas["help"]
    for label, value in areas["choices"].items():
        group = ("Basic", "Basis") if value in BASIC else ("Extended", "Erweitert")
        assert group[0] in label and group[1] in label, value
    for key, (area, libraries) in LIBRARY_QUESTIONS.items():
        question = questions[key]
        assert question["when"] == f"{{{{ '{area}' in test_areas }}}}", key
        assert set(question["choices"].values()) == libraries | {"other", "none"}, key  # other = own, none = back
        assert any("Zurück" in label for label in question["choices"]), key
        assert any("eigene Bibliothek" in label for label in question["choices"]), key
    assert set(questions["ci_provider"]["choices"].values()) == {"gitlab", "github", "none"}
    assert questions["ci_provider"]["default"] == "gitlab"
    for area, switch in AREAS.items():
        assert questions[switch]["when"] is False, switch
        assert f"'{area}' in test_areas" in questions[switch]["default"], switch
    allowed = {"language", "project_name", "project_slug", "rf_version", "python_version", "test_areas", *LIBRARY_QUESTIONS,
               "ci_provider", "include_gitlab_ci", "include_github_ci", "own_library_areas", "use_browser",
               "use_selenium", "use_pages", "use_db_server", *AREAS.values()}
    assert {k for k in questions if not k.startswith("_")} == allowed


@pytest.mark.parametrize(
    ("answers", "web_present"),
    [({"test_areas": ["web"]}, True), ({"test_areas": []}, False),
     ({"test_areas": ["web"], "web_library": "none"}, False)],
    ids=["selected", "not-selected", "back"],
)
def test_back_on_library_acts_like_deselecting(render_project, answers, web_present):
    project = render_project(**answers)
    assert (project / "tests/web").exists() is web_present
    assert ("robotframework-browser" in read(project, "pyproject.toml")) is web_present


def test_area_selection_determines_files(render_project):
    project = render_project(test_areas=["api", "faker", "sap"], api_library="restinstance")
    for switch in ["include_api", "include_faker", "include_sap"]:
        for rel_path in OPTIONS[switch]:
            assert (project / rel_path).exists(), f"Missing: {rel_path}"
    for rel_path in OPTIONS["include_web"] + OPTIONS["include_database"] + OPTIONS["include_desktop"]:
        assert not (project / rel_path).exists(), f"Unexpected: {rel_path}"
    answers = yaml.safe_load(read(project, ".copier-answers.yml"))
    assert answers["test_areas"] == ["api", "faker", "sap"]
    assert "RESTinstance" in read(project, "pyproject.toml")


@pytest.mark.parametrize(
    ("case_data", "area", "folder", "package"),
    [({"test_areas": ["web"], "web_library": "other"}, "web", "tests/web", "robotframework-browser"),
     ({"test_areas": ["api"], "api_library": "other"}, "API", "tests/api", "robotframework-requests"),
     ({"test_areas": ["database"], "database_driver": "other"}, "database", "tests/database",
      "robotframework-databaselibrary")],
    ids=["web", "api", "database"],
)
def test_own_library_creates_no_examples_but_hints(render_project, case_data, area, folder, package):
    project = render_project(**case_data)
    assert not (project / folder).exists()
    assert package not in read(project, "pyproject.toml")
    hint = f"**{area}**"
    assert hint in read(project, "README.md") and "Own library planned" in read(project, "README.md")
    skill = read(project, ".agents/skills/robot-project/SKILL.md")
    assert "different or own library" in skill and hint in skill


def test_no_own_library_no_hint(render_project):
    project = render_project(test_areas=["web", "api"])
    assert "Own library planned" not in read(project, "README.md")
    assert "different or own library" not in read(project, ".agents/skills/robot-project/SKILL.md")


# ----------------------------------------------------------------------------- Files
def test_default_answers(render_project):
    project = render_project()
    for rel_path in CORE + OPTIONS["include_web"] + [".gitlab-ci.yml"]:
        assert (project / rel_path).exists(), f"Missing: {rel_path}"
    for key, paths in OPTIONS.items():
        if key != "include_web":
            for rel_path in paths:
                if rel_path not in OPTIONS["include_web"]:
                    assert not (project / rel_path).exists(), f"Unexpected: {rel_path}"


@pytest.mark.parametrize("option", list(OPTIONS))
def test_each_option_creates_exactly_its_files(render_project, option):
    project = render_project(**{**ALL_NO, option: True})
    for rel_path in CORE + OPTIONS[option]:
        assert (project / rel_path).exists(), f"Missing: {rel_path}"
    for other, paths in OPTIONS.items():
        if other != option:
            for rel_path in paths:
                if rel_path not in OPTIONS[option]:
                    assert not (project / rel_path).exists(), f"Unexpected: {rel_path}"


def test_nothing_selected_gives_only_the_basics(render_project):
    project = render_project(**ALL_NO, ci_provider="none")
    for rel_path in CORE:
        assert (project / rel_path).exists(), f"Missing: {rel_path}"
    robot_files = sorted(p.relative_to(project).as_posix() for p in project.rglob("*.robot"))
    assert robot_files == ["tests/core/credentials.robot"]
    assert not (project / ".gitlab-ci.yml").exists()


@pytest.mark.parametrize(
    "case_data",
    [{}, ALL_NO, ALL_YES, {**ALL_YES, "web_library": "selenium", "api_library": "restinstance",
                                 "database_driver": "mysql", "language": "en"}],
    ids=["default", "all-no", "all-yes", "variants"],
)
def test_no_jinja_leftovers_and_no_forbidden_characters(render_project, case_data):
    project = render_project(**case_data)
    assert_no_jinja_leftovers(project)
    assert_no_forbidden_filename_chars(project)


# ----------------------------------------------------------------------------- Screenplay rules
def test_screenplay_rules(render_project):
    project = render_project(**ALL_YES)
    resources = project / "resources"
    for file in (resources / "abilities").glob("*.resource"):
        text = file.read_text(encoding="utf-8")
        assert "*** Keywords ***" not in text, f"Ability with keywords: {file.name}"
        assert text.count("Resource ") == 1 and "Resource            ${EXECDIR}/resources/main.resource" in text, file.name
    for file in resources.rglob("*.resource"):
        text = file.read_text(encoding="utf-8")
        if file.parent.name not in {"abilities"} and file.name != "main.resource":
            assert not re.search(r"^Library ", text, flags=re.M), f"Library import outside abilities: {file.name}"
        assert not re.search(r"^\s+[$@&]\{[^}]+\}=", text, flags=re.M), f"Assignment with '=' in {file.name}"
        assert not re.search(r"^\s+(Sleep|Evaluate|Convert To Boolean)\b", text, flags=re.M), file.name
    for layer in ["tasks", "assertions"]:
        for file in (resources / layer).glob("*.resource"):
            imports = re.findall(r"^Resource\s+(\S+)", file.read_text(encoding="utf-8"), flags=re.M)
            assert imports and all("/interactions/" in i for i in imports), f"{layer}: {file.name} {imports}"
    for file in (project / "tests").rglob("*.robot"):
        imports = re.findall(r"^Resource\s+(\S+)", file.read_text(encoding="utf-8"), flags=re.M)
        assert imports and all(("/tasks/" in i) or ("/assertions/" in i) for i in imports), f"{file} {imports}"
    for file in (resources / "pages").glob("*.resource"):
        assert "*** Keywords ***" not in file.read_text(encoding="utf-8"), file.name


def test_main_resource_contains_basics(render_project):
    main = read(render_project(include_api=True), "resources/main.resource")
    for expected in ["Library             Collections", "Library             String", "Library             CryptoLibrary",
                     "key_path=${EXECDIR}/data/keys", "${CI}                   False", "${TIMEOUT}",
                     "${BROWSER}", "&{URLS}", "dev=${URLS_DEV}", "test=${URLS_TEST}", "prod=${URLS_PROD}",
                     "&{LOGINS}", "web=https://", "api=https://"]:
        assert expected in main, expected


# ----------------------------------------------------------------------------- Packages and execution
def test_only_robot_framework_is_pinned(render_project):
    pyproject = read(render_project(**ALL_YES), "pyproject.toml")
    pins = re.findall(r'"([A-Za-z0-9_.\[\]-]+)==', pyproject)
    assert pins == ["robotframework"], pins
    assert f'"robotframework=={RF_VERSION}"' in pyproject
    for package in ["robotframework-crypto", "robotframework-robocop", "robotcode[runner]"]:
        assert f'"{package}"' in pyproject


@pytest.mark.parametrize(
    ("case_data", "present", "absent"),
    [
        ({"web_library": "browser"}, "robotframework-browser", "seleniumlibrary"),
        ({"web_library": "selenium"}, "robotframework-seleniumlibrary", "robotframework-browser"),
        ({"include_web": False, "include_api": True, "api_library": "restinstance"}, "RESTinstance", "robotframework-requests"),
        ({"include_database": True, "database_driver": "postgresql"}, "psycopg2-binary", "pymysql"),
        ({"include_database": True, "database_driver": "mysql"}, "pymysql", "psycopg2"),
        ({"include_database": True, "database_driver": "sqlite"}, "robotframework-databaselibrary", "psycopg2"),
        ({"include_email": True}, "robotframework-imaplibrary2", "doctestlibrary"),
    ],
)
def test_variants_install_the_right_packages(render_project, case_data, present, absent):
    pyproject = read(render_project(**case_data), "pyproject.toml")
    assert present in pyproject and absent not in pyproject


def test_database_server_has_connection_test_and_profile(render_project):
    with_server = render_project(include_database=True, database_driver="mysql")
    assert (with_server / "tests/database/connection.robot").exists()
    assert re.search(r"^\$\{DB_MODULE\}\s+pymysql$", read(with_server, "resources/abilities/database_ability.resource"), flags=re.M)
    assert "[profiles.database]" in read(with_server, "robot.toml")


def test_sqlite_has_no_connection_test(render_project):
    without_server = render_project(include_database=True, database_driver="sqlite")
    assert not (without_server / "tests/database/connection.robot").exists()
    assert "[profiles.database]" not in read(without_server, "robot.toml")


def test_device_tests_are_excluded_but_checked(render_project):
    toml = read(render_project(**ALL_YES, database_driver="postgresql"), "robot.toml")
    assert ('excludes = ["requires-device", "requires-desktop", "requires-mailbox", "requires-database", "requires-sap"]'
            in toml)
    assert re.search(r"\[profiles\.check\]\n[^\[]*dry-run = true\nexcludes = \[\]", toml)
    for profile in ["mobile", "desktop", "email", "database", "sap", "headed", "ci", "dev", "test", "prod"]:
        assert f"[profiles.{profile}]" in toml, profile


def test_gitignore_and_gitlab_ci(render_project):
    project = render_project(include_accessibility=True)
    gitignore = read(project, ".gitignore")
    for entry in [".venv/", "results/", "playwright-log.txt", "data/keys/private_key*", ".env", "node_modules/"]:
        assert entry in gitignore, entry
    ci = yaml.safe_load(read(project, ".gitlab-ci.yml"))
    assert set(ci) >= {"check", "test"}
    assert "uv run robotcode -p ci robot" in ci["test"]["script"]


DOC_PAIRS = [("README.md", "README.de.md")] + [
    (f"docs/{name}.md", f"docs/{name}.de.md") for name in ["getting-started", "generated-projects", "versions-and-updates"]]


def test_no_long_dashes(render_project):
    docs = [TEMPLATE_ROOT / name for pair in DOC_PAIRS for name in pair]
    for file in list((TEMPLATE_ROOT / "template").rglob("*")) + docs + [TEMPLATE_ROOT / "copier.yml"]:
        if file.is_file() and file.suffix not in {".png", ".pdf"}:
            text = file.read_text(encoding="utf-8", errors="ignore")
            assert "\u2013" not in text and "\u2014" not in text, file


@pytest.mark.parametrize(("english_path", "german_path"), DOC_PAIRS, ids=[pair[0] for pair in DOC_PAIRS])
def test_user_docs_exist_in_english_and_german_with_the_same_structure(english_path, german_path):
    english = (TEMPLATE_ROOT / english_path).read_text(encoding="utf-8")
    german = (TEMPLATE_ROOT / german_path).read_text(encoding="utf-8")
    assert f"[Deutsch]({Path(german_path).name})" in english.splitlines()[2]
    assert f"[English]({Path(english_path).name})" in german.splitlines()[2]
    for level in ["## ", "### "]:
        count = [sum(line.startswith(level) for line in text.splitlines()) for text in (english, german)]
        assert count[0] == count[1], (level, count)
    for command in re.findall(r"^uvx copier \S+ .*$", english, flags=re.M):
        options = re.sub(r"--data-file \S+", "--data-file", command.split("#")[0].split(" https://")[0].strip())
        assert options in re.sub(r"--data-file \S+", "--data-file", german), command


def test_readme_stays_short_and_links_existing_pages():
    for name in ["README.md", "README.de.md"]:
        assert len((TEMPLATE_ROOT / name).read_text(encoding="utf-8").splitlines()) <= 80, name
    for pair in DOC_PAIRS:
        for name in pair:
            file = TEMPLATE_ROOT / name
            for link in re.findall(r"\]\(([^)#:]+\.(?:md|yml))(?:#[^)]*)?\)", file.read_text(encoding="utf-8")):
                assert (file.parent / link).resolve().exists(), f"{name}: {link}"


def test_intro_shows_the_central_version():
    text = (TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8")
    questions = yaml.safe_load(text)
    assert f'set version = "{questions["rf_version"]["default"]}"' in questions["_message_before_copy"]
    assert "Immer dabei" in questions["_message_before_copy"]
    assert "Enter = Auswahl bestätigen" in questions["_message_before_copy"]


def test_project_name_defaults_to_folder_name(tmp_path):
    target = tmp_path / "kundenportal-tests"
    run_copy(str(TEMPLATE_ROOT), str(target), vcs_ref="HEAD", defaults=True, overwrite=True, unsafe=True, skip_tasks=True, quiet=True)
    answers = yaml.safe_load(read(target, ".copier-answers.yml"))
    assert answers["project_name"] == "kundenportal-tests"
    assert "# kundenportal-tests" in read(target, "README.md")


def test_overview_shows_target_folder():
    questions = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))
    assert questions["project_name"]["default"] == "{{ _folder_name }}"
    overview = questions["_message_before_copy"]
    assert "Ziel / target" in overview and "{{ _folder_name }}" in overview
    # Copier captures the mouse wheel during the dialog: the overview must fit into a small window
    shown = [line for line in overview.splitlines() if line.strip() and not line.lstrip().startswith("{%")]
    assert len(shown) <= 10, len(shown)
    assert "_copier_conf.dst_path | string != '.'" in questions["_message_after_copy"]  # no "cd ." in the final message
    assert "own_library_areas" in questions["_message_after_copy"]


def test_final_message_explains_next_steps_and_skills():
    final_message = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))["_message_after_copy"]
    for expected in ["uv run robotcode robot", ".agents/skills/", "robot-write-test", "Coding assistants",
                     "Agent Skills", "uv add <package>", "uv add <paket>"]:
        assert expected in final_message, expected


def test_agent_skills_have_valid_format(render_project):
    project = render_project(**ALL_YES)
    folder = sorted((project / ".agents/skills").iterdir())
    assert [o.name for o in folder] == ["robot-explain-results", "robot-project", "robot-write-test"]
    for skill in folder:
        text = read(skill, "SKILL.md")
        assert text.startswith("---\n"), skill.name
        front_matter = yaml.safe_load(text.split("---\n")[1])
        assert front_matter["name"] == skill.name
        assert re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", front_matter["name"]) and len(front_matter["name"]) <= 64
        assert 0 < len(front_matter["description"]) <= 1024, skill.name


def test_agent_skills_name_selected_libraries_and_no_internal_data(render_project):
    project = render_project(include_api=True, api_library="restinstance", include_email=True)
    skills = project / ".agents/skills"
    project_skill = read(skills, "robot-project/SKILL.md")
    for expected in [f"Robot Framework {RF_VERSION}", "Browser Library (Playwright)", "RESTinstance", "ImapLibrary2",
                     "crypt:", "https://marketsquare.github.io/robotframework-browser/Browser.html",
                     "ask as little as possible", "interaction", "In a chat without file access"]:
        assert expected in project_skill, expected
    for missing in ["SeleniumLibrary |", "RequestsLibrary |", "PlatynUI |", "FakerLibrary |"]:
        assert missing not in project_skill, missing
    test_case_skill = read(skills, "robot-write-test/SKILL.md")
    for expected in ["keyword-driven", "The test is the specification", "Reuse instead of sentence building",
                     "Log In", "Fetch Todo", "at most one question", "no\n`Given`/`When`/`Then` prefixes"]:
        assert expected in test_case_skill, expected
    assert "Given:" not in test_case_skill
    assert "Generate Random Customer" not in test_case_skill
    assert "application" in read(skills, "robot-explain-results/SKILL.md")
    for skill in skills.rglob("SKILL.md"):
        assert not re.search(r"[\w.-]+@(?!example\.)[\w-]+\.[a-z]{2,}", read(skill, "")), skill


def test_every_skill_works_on_its_own_in_a_chat(render_project):
    project = render_project(**ALL_YES)
    for skill in (project / ".agents/skills").iterdir():
        text = read(skill, "SKILL.md")
        assert "Works in the IDE and when pasted into a chat" in " ".join(text.split()), skill.name
        assert f"Robot Framework {RF_VERSION}" in text, skill.name
        for layer in ["resources/tasks/", "resources/assertions/", "resources/interactions/", "resources/pages/"]:
            assert layer in text, (skill.name, layer)
    write_test = read(project, ".agents/skills/robot-write-test/SKILL.md")
    assert "complete, copyable blocks" in write_test and "Keyword Tags  interaction" in write_test


# ----------------------------------------------------------------------------- README
def test_readme_names_selected_libraries_and_finished_setup(render_project):
    readme = read(render_project(include_api=True, api_library="restinstance", include_faker=True), "README.md")
    for expected in ["Browser Library (Playwright)", "RESTinstance", "FakerLibrary", "CryptoLibrary",
                     "already set up", "rfbrowser init chromium", "Screenplay", "Setup and teardown",
                     "https://robotcode.io/03_reference/config", "Adding more libraries", "uv add <package>",
                     "_src_path", "BROWSER_SPEED", "Coding assistants (Agent Skills)", ".agents/skills/",
                     "Keyword Tags    interaction", f"--vcs-ref rf-{RF_VERSION}"]:
        assert expected in readme, expected
    for missing in ["SeleniumLibrary |", "RequestsLibrary |", "PlatynUI |", "ImapLibrary2 |"]:
        assert missing not in readme, missing


# ----------------------------------------------------------------------------- Real runs (internet needed)
def _generate(target, **case_data):
    case_data.setdefault("project_name", "Test Project")
    run_copy(str(TEMPLATE_ROOT), str(target), vcs_ref="HEAD", data=case_data, defaults=True, unsafe=True)


@pytest.mark.slow
@pytest.mark.parametrize(
    "case_data",
    [
        ALL_YES,
        {**ALL_YES, "web_library": "selenium", "api_library": "restinstance", "database_driver": "mysql",
         "language": "en"},
    ],
    ids=["playwright-requests", "selenium-restinstance"],
)
def test_project_runs_and_passes_robocop(short_path, case_data):
    """Generate a project like a user does (with setup) and run all default tests."""
    target = short_path / "project"
    _generate(target, **case_data)
    subprocess.run(["uv", "run", "robocop", "check"], cwd=target, check=True)
    subprocess.run(["uv", "run", "robotcode", "robot"], cwd=target, check=True)


def test_imports_always_start_from_execdir(render_project):
    project = render_project(**ALL_YES)
    for file in list((project / "resources").rglob("*.resource")) + list((project / "tests").rglob("*.robot")):
        text = file.read_text(encoding="utf-8")
        for line in re.findall(r"^(?:Resource|Variables)\s+(\S+)", text, flags=re.M):
            assert line.startswith("${EXECDIR}/"), f"{file.name}: {line}"
        assert "${CURDIR}" not in text and "../" not in text, file.name


def test_browser_library_is_imported_only_once(render_project):
    project = render_project(include_web=True, web_library="browser", include_accessibility=True)
    with_browser = [d.name for d in (project / "resources").rglob("*.resource")
                   if re.search(r"^Library\s+Browser\b", d.read_text(encoding="utf-8"), flags=re.M)]
    assert with_browser == ["browser_ability.resource"], with_browser
    assert "jsextension=${EXECDIR}/resources/axe_extension.js" in read(project, "resources/abilities/browser_ability.resource")
    assert read(project, "pyproject.toml").count("robotframework-browser") == 1


def test_accessibility_alone_brings_the_browser_layer(render_project):
    project = render_project(include_web=False, include_accessibility=True)
    for rel_path in [*BROWSER_LAYER, *PAGES]:
        assert (project / rel_path).exists(), rel_path
    assert not (project / "resources/tasks/web_tasks.resource").exists()
    assert "robotframework-browser" in read(project, "pyproject.toml")


def test_selenium_and_accessibility_side_by_side(render_project):
    project = render_project(web_library="selenium", include_accessibility=True)
    assert (project / "resources/abilities/selenium_ability.resource").exists()
    assert (project / "resources/abilities/browser_ability.resource").exists()
    assert "selenium_interactions.resource" in read(project, "resources/tasks/web_tasks.resource")
    assert "New Browser    chromium" in read(project, "resources/interactions/browser_interactions.resource")


def test_robot_framework_version_only_in_copier_yml():
    questions = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))
    assert questions["rf_version"]["when"] is False
    for file in (TEMPLATE_ROOT / "template").rglob("*"):
        if file.is_file() and file.suffix not in {".png", ".pdf"}:
            text = file.read_text(encoding="utf-8", errors="ignore")
            assert questions["rf_version"]["default"] not in text, file
            python = re.escape(questions["python_version"]["default"])
            assert not re.search(rf"(?<![<\d.]){python}(?!\d)", text), file


def test_python_version_comes_from_copier_yml(render_project):
    python = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))["python_version"]["default"]
    project = render_project()
    assert read(project, ".python-version").strip() == python
    assert f'requires-python = ">={python}"' in read(project, "pyproject.toml")
    assert f'requires-python = ">={python},<3.14"' in read(render_project(include_desktop=True), "pyproject.toml")


def test_project_is_english(render_project):
    project = render_project(**ALL_YES, ci_provider="github")
    for file in project.rglob("*"):
        if file.is_file() and file.suffix not in {".png", ".pdf"}:
            text = file.read_text(encoding="utf-8", errors="ignore")
            assert not re.search("[äöüßÄÖÜ]", text), file
        assert not re.search("[äöüß]", file.name), file


def test_interactions_are_tagged_and_never_used_in_tests(render_project):
    project = render_project(**ALL_YES)
    interaction_keywords = set()
    for file in (project / "resources/interactions").glob("*.resource"):
        text = file.read_text(encoding="utf-8")
        assert re.search(r"^Keyword Tags\s+interaction$", text, flags=re.M), file.name
        interaction_keywords |= set(re.findall(r"^(\S.*)$", text.split("*** Keywords ***")[1], flags=re.M))
    assert "Launch Browser" in interaction_keywords and "Run Sql" in interaction_keywords
    for file in (project / "tests").rglob("*.robot"):
        for line in file.read_text(encoding="utf-8").splitlines():
            step = re.split(r"\s{2,}", line.strip())
            assert not set(step) & interaction_keywords, f"{file.name}: {line.strip()}"


def test_tasks_and_assertions_do_not_hide_library_keywords(render_project):
    project = render_project(**ALL_YES)
    library_keywords = {"close browser", "open browser", "wait for email", "close mailbox", "connect to database",
                        "disconnect from database", "go to", "click", "get text", "close application",
                        "close all applications", "open application", "execute transaction", "get window title",
                        "close sap", "compare images", "name", "email", "city"}
    for layer in ["tasks", "assertions"]:
        for file in (project / "resources" / layer).glob("*.resource"):
            text = file.read_text(encoding="utf-8").split("*** Keywords ***")[1]
            for keyword in re.findall(r"^(\S.*)$", text, flags=re.M):
                assert keyword.lower() not in library_keywords, f"{file.name}: {keyword}"


def test_pages_without_xpath_and_with_underscore_names(render_project):
    project = render_project(include_accessibility=True)
    for file in (project / "resources/pages").glob("*.resource"):
        assert file.name.endswith("_page.resource"), file.name
        assert "xpath" not in file.read_text(encoding="utf-8").lower(), file.name


def test_vscode_uses_the_project_environment(render_project):
    settings = read(render_project(), ".vscode/settings.json")
    assert ".venv" in settings and "python.defaultInterpreterPath" in settings


def test_profiles_have_descriptions(render_project):
    toml = read(render_project(**ALL_YES), "robot.toml")
    assert toml.count("[profiles.") == toml.count("description = ")
    assert 'BROWSER_SPEED = "0.5s"' in toml


def test_template_paths_are_short_enough_for_windows():
    """Copier clones the template into a deep temp folder; Windows allows 260 characters by default."""
    for file in (TEMPLATE_ROOT / "template").rglob("*"):
        relative = file.relative_to(TEMPLATE_ROOT).as_posix()
        assert len(relative) <= 115, f"{len(relative)} characters: {relative}"


def test_gitlab_ci_reports_template_updates_without_failing(render_project):
    ci = yaml.safe_load(read(render_project(), ".gitlab-ci.yml"))
    job = ci["template-check"]
    assert job["allow_failure"] is True and job["stage"] == "check"
    rf_version = yaml.safe_load((TEMPLATE_ROOT / "copier.yml").read_text(encoding="utf-8"))["rf_version"]["default"]
    assert "refs/heads/$BRANCH" in job["script"][0] and f'BRANCH="rf-{rf_version}"' in job["script"][0]


def test_github_actions_instead_of_gitlab(render_project):
    project = render_project(ci_provider="github", include_accessibility=True)
    assert not (project / ".gitlab-ci.yml").exists()
    workflow = yaml.safe_load(read(project, ".github/workflows/robot.yml"))
    assert set(workflow["jobs"]) == {"check", "test", "template-check"}
    assert workflow["jobs"]["template-check"]["continue-on-error"] is True
    steps = " ".join(str(step.get("run", "")) for step in workflow["jobs"]["test"]["steps"])
    assert "uv run robotcode -p ci -p ${{ inputs.environment || 'dev' }} robot" in steps and "npm ci" in steps
    assert "github.vscode-github-actions" in read(project, ".vscode/extensions.json")
    assert "## GitHub Actions" in read(project, "README.md") and "## GitLab CI" not in read(project, "README.md")


def test_no_ci_pipeline(render_project):
    project = render_project(ci_provider="none")
    assert not (project / ".gitlab-ci.yml").exists() and not (project / ".github").exists()


@pytest.mark.parametrize("ci_provider", ["gitlab", "github", "none"])
def test_vscode_extensions_are_valid_json(render_project, ci_provider):
    import json

    extensions = json.loads(read(render_project(ci_provider=ci_provider), ".vscode/extensions.json"))
    assert extensions["recommendations"][:2] == ["d-biehl.robotcode", "ms-python.python"]
    assert "tamasfe.even-better-toml" not in extensions["recommendations"]
