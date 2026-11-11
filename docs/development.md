# Developing the template

This repository is a **Copier template**. Through a dialog in the terminal it creates ready-to-run Robot
Framework projects (web, API, e-mail, database, desktop, mobile, test data, PDF/images, SAP, accessibility -
freely combinable).

What the template does and the decisions behind it are described in `docs/specification.md`. This file
collects the conventions the template follows and the commands for working on it. Deviations for technical
reasons are explained in `CHANGELOG.md`.

## Guiding idea

The template should make **starting a project easy**: a short dialog, followed by a plain, immediately
runnable structure. New questions, files, tools or switches are only added when they clearly improve that
start; between two solutions the simpler one usually wins.

## Who the template is built for

1. **People developing the template** - technically experienced, working in this repository.
2. **People using a generated project** - explicitly including **business people without programming
   experience**. That is why everything in `template/` (Robot files, README, Agent Skills) uses plain
   language, business names and explained technical terms.

## Repository layout

```text
copier.yml                  dialog (English/German), conditions, setup steps, coloured texts
template/                   everything that ends up in the generated project (_subdirectory)
  README.md.jinja           project README for beginners
  resources/                main.resource and the Screenplay layers (one file per library)
  tests/                    hello world tests per library (+ tests/core always)
  data/keys/                folder for the CryptoLibrary keys
  robot.toml.jinja          single source of execution options (profiles)
  pyproject.toml.jinja      packages; only Robot Framework has a fixed version
  .agents/skills/           Agent Skills for coding assistants (always included, no internal data)
tests/                      pytest: dialog, files, rules, real runs (slow), matrix (matrix)
docs/specification.md       description of the template and its decisions
docs/getting-started*.md    user docs: creating a project, dialog, troubleshooting (EN/DE)
docs/generated-projects*.md user docs: structure, Agent Skills, more libraries (EN/DE)
docs/versions-and-updates*.md user docs: Robot Framework versions, updates, own copy (EN/DE)
docs/development.md         this file
README.md, README.de.md     short start page in English and German (not copied into projects)
.github/                    tests on push/PR, weekly version check (workflow + script), Dependabot
```

## Commands

```bash
uv sync                                         # development environment (copier, pytest)
uv run pytest -m "not slow and not matrix"      # dialog, files, rules (fast)
uv run pytest -m slow                           # generate real projects and run them (internet)
uv run pytest -m matrix                         # many answer combinations (about 20 min)
```

To try the template by hand, generate into a folder **outside** the repository. `--vcs-ref HEAD` uses the
working copy including uncommitted changes (without it, Copier takes the latest tag):

```bash
mkdir C:/Temp/probe && cd C:/Temp/probe
uvx copier copy --trust --defaults --vcs-ref HEAD --data-file C:/Projects/robotframework-copiertemplates/tests/data/full.yml C:/Projects/robotframework-copiertemplates .
```

## Conventions

### Copier and Jinja

- Keep the dialog short. All areas are picked in **one** multi-select list (`test_areas`); "basic" and
  "extended" only group the entries. A follow-up question only exists where there is a real choice:
  `web_library`, `api_library` and `database_driver`, each with "Other / own library" (`other`) and "↩ Back"
  (`none`). Areas with a single library ask nothing. `copier.yml` computes the switches `include_*`
  (`when: false`) and `own_library_areas`; `ci_provider` (gitlab, github, none) sets `include_gitlab_ci` /
  `include_github_ci`.
- The dialog assumes it runs in the project folder (target `.`): the overview shows the target folder,
  `project_name` suggests its name (`_folder_name`).
- A new question touches several places: `copier.yml` (help text in English **and** German via `language`),
  the dialog description in `docs/getting-started.md` and `docs/getting-started.de.md`, the tests in `tests/` and, if needed, a migration for
  `copier update`. These changes belong in the same commit.
- Conditional files and folders are created via names that render empty, for example
  `{% if include_web %}web_tasks.resource{% endif %}`. Only files with Jinja content end in `.jinja`.
- File names contain no `|` filters and none of the characters `< > : " \ | ? *`, otherwise the repository
  cannot be checked out on Windows.
- Whitespace control (`{%-`, `-%}`) is set so that generated files pass Robocop without findings and contain
  no Jinja leftovers (both are tested).
- **Only Robot Framework and Python have fixed versions** - in exactly one place per branch, `rf_version` and
  `python_version` in `copier.yml` (computed, not stored, so they are re-evaluated on every `copier update`). The
  template contains neither a literal `7.x.y` nor `3.x` Python version (test). uv resolves the libraries; `uv.lock` in the generated project freezes them.
- Long conditions live as computed variables in `copier.yml` (`use_browser`, `use_selenium`, `use_pages`,
  `use_db_server`), not in file names: paths in the template are at most 115 characters (test), otherwise
  checkout fails on Windows.
- When answers change meaning in a later version (renamed keys, moved choices), add a Copier migration
  (`_migrations` in `copier.yml`, script in a folder `migrations/`). Make it idempotent and let it run on every
  update - the `rf-*` branches have no version tags of their own, so version-bound migrations would not run
  there. Test it by updating a project generated from the previous version.
- The generated project has a `.gitattributes` with LF line endings, so that `copier update` shows conflicts
  only on lines that really changed.

### Robot Framework versions and branches

- `master` carries the newest supported Robot Framework version; every version has a branch
  `rf-<version>` (the newest one equals `master`). Every `rf-*` branch gets its own tags
  `v<version>+rf<rf_version>`, so that Copier orders versions correctly across branches (otherwise it reports
  a downgrade when a project moves to a newer Robot Framework version).
- The version is never raised automatically. `.github/workflows/dependency-check.yml` reports new releases
  as an issue; raising follows docs/versions-and-updates.md, "Adding a new Robot Framework version".
- Fixes that should also reach older versions are cherry-picked onto their `rf-*` branches.

### Screenplay structure in the template (without actor)

- `resources/main.resource`: standard libraries (Collections, DateTime, OperatingSystem, Process, String) and
  CryptoLibrary (`key_path=${EXECDIR}/data/keys`), URLs (`URLS`) and credentials (`LOGINS`) per environment
  dev/test/prod, global values (`${ENV}`, `${CI}`, `${TIMEOUT}`, `${BROWSER}` …).
- `resources/abilities/`: one file per library with `Resource ${EXECDIR}/resources/main.resource`, the
  `Library` import and the variables the library needs - **no keywords**.
- `resources/pages/`: page objects, one file per page, variables `PAGE_ELEMENT`, no keywords.
- `resources/interactions/`: technical helper keywords; **the only place with library keywords**; import
  ability (and page); every file has `Keyword Tags    interaction`.
- `resources/tasks/`: business actions with imperative names and arguments (also setup and teardown such as
  `Start Browser`); import interactions only.
- `resources/assertions/`: **generic** checks (`Element Should Show Text`, `Status Code Should Be`);
  `core_assertions` is always included.
- Tests are **keyword-driven**: each line is a task or an assertion, no Given/When/Then prefixes.
- All keywords, test names, documentation and file names are English. Keywords that do not belong in tests
  (interactions) carry the tag `interaction`; a test checks that tests never call them. `robot:private` is not
  used: Robot Framework warns whenever a private keyword is called from another file.
- Task and assertion names must not equal library keyword names (e.g. not `Close Browser`, `Wait For Email`):
  the own keyword would hide the library keyword and the interaction would call itself.
- Browser Library: one shared layer (`browser_ability`, `browser_interactions`) for web and accessibility,
  the library is imported only once. Pages are named `<page>_page.resource`, selectors use `id`/`data-test`,
  not XPath.
- `tests/` imports only tasks and assertions.
- All imports (`Resource`, `Variables`) and paths start from `${EXECDIR}` (project folder), never relative
  with `../` and never via `${CURDIR}`. Tests are therefore always started in the project folder.
- Variants (Browser/Selenium, Requests/RESTinstance) differ only in ability and interactions; tasks,
  assertions and tests are identical.
- Every keyword has a `[Documentation]` written for business readers. Assignments without `=`, `VAR`
  instead of `Set Variable`, no `Sleep` and no `Evaluate` - waiting happens via wait or assertion keywords.
- Every library has at least one hello world test. Tests that need a device, program, mailbox or server
  (`requires-device`, `requires-desktop`, `requires-mailbox`, `requires-database`, `requires-sap`) are excluded
  by default and run with their profile. The others use public web pages, open APIs or in-memory SQLite (no
  mocks).

### Execution

- `robot.toml` is the single source of execution options. Locally, in the IDE and in GitLab CI or GitHub Actions everything
  runs via `uv run robotcode -p <profile> ... robot`.
- If CI needs a new combination, a new profile is added; `.gitlab-ci.yml` and `.github/workflows/robot.yml` contain no Robot options.

### Documentation

- User documentation exists in English and German: `README.md` / `README.de.md` (short start page) and
  `docs/<topic>.md` / `docs/<topic>.de.md` (getting started, generated projects, versions and updates). Change
  both languages in the same commit (a test compares their structure). Maintainer documentation
  (`docs/development.md`, `docs/specification.md`, `CHANGELOG.md`) is English only.
- Changes that affect users of generated projects are reflected in the same commit in
  `template/README.md.jinja` and in the Agent Skills in `template/.agents/skills/`.
- Sections and links appear only for selected libraries.
- Everything is written in English: repository documentation and the generated projects (README, skills,
  keywords, comments). Only the dialog offers German as a second language.

### Data and security

- The Agent Skills use the open format (folder `.agents/skills/`), are not tied to any tool and contain no
  internal data.
- CryptoLibrary keys live in `data/keys/`; the private key is listed in `.gitignore`.
- Template and tests contain no credentials, tokens, keys or real personal data. Placeholders in
  `main.resource` are obviously fake.

## Workflow for a change
- A change is done when the tests are green (locally and in the `Tests` workflow on GitHub); it ends with a
  short commit message.
  protected: changes go through a pull request with green `Tests` workflow.
- New libraries are checked first (PyPI, official documentation, compatibility with the branch's Python version and the
  current Robot Framework version); the result goes into `CHANGELOG.md`.
- Points marked **[open]** in the specification are decided together.
- What cannot be tested locally (Appium, SAP, mailbox, database server) is noted as untested in
  `CHANGELOG.md`.
- Installations run via `uv`, never globally (`pip install`, `npm -g`).
- Generated test projects are not committed (only under pytest's `tmp_path` or outside the repository).
- Tests are not weakened or skipped to make a pipeline green.
