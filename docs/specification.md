# robotframework-copiertemplates - Specification

Version 1.0 · 2026-11-11

A repository from which anyone can create a ready-to-run Robot Framework project with **one command** and a
short dialog - set up, with example tests for every library, understandable for business people. The guiding
idea is simplicity: a short dialog with one selection list, followed by a plain, immediately runnable
project structure based on the Screenplay pattern.

| Technology | |
|---|---|
| Python | one fixed version per branch (`python_version`, currently 3.13), matching Robot Framework and the libraries |
| Robot Framework | one fixed version per branch (`master`: newest, `rf-<version>`: older versions) |
| Package management | uv |
| Template engine | Copier (9.4 or newer) |
| Execution | RobotCode with profiles in `robot.toml` |
| Linting | Robocop |
| CI / IDE | GitLab CI or GitHub Actions / VS Code |

## §1 Goal

After `uvx copier copy --trust <repo-url> .` in the project folder, the user has:

- a Git repository with a ready Python environment (`.venv`, `uv.lock`),
- the Screenplay structure in `resources/` with files only for the selected libraries,
- at least one passing hello world test per library (plus `tests/core`, always),
- a beginner-friendly README, VS Code recommendations, `.gitignore`,
- Agent Skills for coding assistants in `.agents/skills/` (no internal data),
- optionally: a CI pipeline for GitLab CI or GitHub Actions.

**Out of scope:** installing Appium, emulators, database servers or SAP GUI; other IDEs and CI systems.

## §2 Decisions

| Topic | Decision |
|---|---|
| Dialog | language selectable (Deutsch/English); one multi-select list of areas grouped into basic and extended (Enter confirms); a library question only for web, API and database, each with "Other / own library" and "↩ Back"; CI: GitLab, GitHub or none |
| Language | generated projects are completely English (keywords, test names, documentation, README, skills) |
| Versions | only Robot Framework is pinned (`rf_version`), one branch per version; never raised automatically. All other libraries are resolved by uv, `uv.lock` freezes them |
| Always installed | Robot Framework, CryptoLibrary, Robocop, RobotCode |
| Python | `python_version` in `copier.yml` per branch (`.python-version`, `requires-python`); with desktop additionally `<3.14` (PlatynUI); raised only after the real tests pass |
| Execution | only `uv run robotcode [-p <profile>] robot` via `robot.toml` |
| Environments | `dev` (default), `test`, `prod` - values as dictionaries in `main.resource` |
| Credentials | CryptoLibrary with `variable_decryption=True`, keys in `data/keys/` |
| Examples | public web pages, open APIs, in-memory SQLite - no mocks |
| Test style | keyword-driven: tests are sequences of business keywords with arguments, no Given/When/Then prefixes |
| Coding assistants | always three Agent Skills in `.agents/skills/` (open format, tool-neutral, also usable as a system prompt) |

## §3 Usage

```bash
cd <project-folder>                                       # e.g. a freshly cloned, empty repository
uvx copier copy --trust <repo-url> .                      # files go straight into this folder
uvx copier copy --trust --vcs-ref rf-7.4.2 <repo-url> .   # same, with an older Robot Framework version
uv run robotcode robot
uvx copier update --trust --vcs-ref rf-<version>          # later; stays on that version
```

The current folder (`.`) is the default. Another path as target creates a new folder instead.

On Windows with the Microsoft Store Python, Copier's Git cache can fail; fix: run `uv python install`
once (details in docs/getting-started.md).

## §4 Dialog

| # | Key | Question | Type | Condition | Default |
|---|---|---|---|---|---|
| 1 | `language` | Dialog language | de / en | - | de |
| 2 | `project_name` | Project name? | text | - | name of the target folder |
| 3 | `test_areas` | What do you want to test? | multi-select, basic: `web`, `api`; extended: `email`, `database`, `faker`, `doctest`, `accessibility`, `desktop`, `mobile`, `sap` | - | `[web]` |
| 4 | `web_library` | Web: which browser library? | `browser` / `selenium` / `other` (own) / `none` (back) | only if `web` is selected | browser |
| 5 | `api_library` | API: which library? | `requests` / `restinstance` / `other` / `none` | only if `api` is selected | requests |
| 6 | `database_driver` | Database: which one? | `sqlite` / `postgresql` / `mysql` / `other` / `none` | only if `database` is selected | sqlite |
| 7 | `ci_provider` | Create a CI pipeline? | `gitlab` / `github` / `none` | - | gitlab |

Help texts and choice labels are Jinja expressions using `language`. A short coloured overview (ANSI,
`_message_before_copy`, at most 10 lines of at most 80 characters) is shown before the dialog: target folder
(files go straight into it; wrong folder: Ctrl+C, change folder, start again), areas and controls ("Enter =
confirm selection" in green), because Copier cannot colour choice lists and has no general "back" to the
previous question. It stays short because Copier captures the mouse wheel while the dialog runs, so the
terminal cannot be scrolled up. A coloured final message in the chosen language lists the next steps, how to use the Agent
Skills and - for "other" - how to add the own library.

Computed (not asked): `include_<area>` = area selected and, for web, API and database, its library neither
"other" nor "back";
`own_library_areas` lists the areas with "other"; `include_gitlab_ci` / `include_github_ci` from `ci_provider`.
The `include_*` keys can still be set directly via `--data`.

Setup after generation (`_tasks`, only with `--trust`): `git init`, `uv sync`,
`uv run rfbrowser init chromium` (Playwright or accessibility), `npm install` (accessibility),
`uv run robotcode -p check robot`.

## §5 Libraries and packages

| Area | Package(s) | Hello world | Runs out of the box? |
|---|---|---|---|
| Basics | `robotframework==<rf_version>`, `robotframework-crypto` | read credentials per environment, hide a password in the log | yes |
| Web | `robotframework-browser` / `robotframework-seleniumlibrary` | demo shop saucedemo.com: log in, add a product to the cart | yes (Selenium: Chrome required) |
| API | `robotframework-requests` / `RESTinstance` | jsonplaceholder: get a todo, filter, create a post | yes |
| Database | `robotframework-databaselibrary` (+ `psycopg2-binary` or `pymysql`) | in-memory SQLite: create, change, delete customers; with a server also a connection test | SQLite yes; server: tag `requires-database` |
| Desktop | `robotframework-platynui` | Windows calculator: 12+30 and 6*7 | no - tag `requires-desktop` |
| Mobile | `robotframework-appiumlibrary` | Android settings: open an entry | no - tag `requires-device` |
| Test data | `robotframework-faker` | generate and check fake customers | yes |
| E-mail | `robotframework-imaplibrary2` | wait for a confirmation mail, check its text | no - tag `requires-mailbox` |
| PDF/images | `robotframework-doctestlibrary` | compare image and PDF with a reference, text in a PDF | yes |
| SAP | `robotframework-robosapiens` | open transaction SU3 | no - tag `requires-sap` |
| Accessibility | `robotframework-browser` + npm `axe-core` | data-driven: pages without serious violations, HTML report per page | yes |

Development tools (group `dev`): `robotcode[runner]`, `robotframework-robocop`. Most libraries are maintained
by the community at [MarketSquare](https://github.com/MarketSquare).

## §6 Screenplay structure (without actor)

```text
tests/<area>/                 test cases                        import only tasks and assertions
resources/tasks/              business actions                  import interactions
resources/assertions/         business checks                   import interactions
resources/interactions/       technical helper keywords         import ability (+ page)
resources/pages/              page objects (selectors)          -
resources/abilities/          library import + settings         import main.resource
resources/main.resource       foundation                        -
```

- **main.resource:** Collections, DateTime, OperatingSystem, Process, String, CryptoLibrary
  (`variable_decryption=True`, `key_path=${EXECDIR}/data/keys`); `${ENV}`, `${CI}`, `${TIMEOUT}`, for
  web/accessibility `${BROWSER}`, `${HEADLESS}`, window size; `&{URLS_DEV|TEST|PROD}` to `&{URLS}`,
  `&{LOGIN_DEV|TEST|PROD}` to `&{LOGINS}`.
- **Abilities:** one file per library, only `Resource ${EXECDIR}/resources/main.resource`, `Library …` and the
  library's variables (server, endpoints, locale …). No keywords. Browser variables do not belong here,
  selectors belong in pages.
- **Pages:** one file per page (`<page>_page.resource`, for PlatynUI `<page>_page.py`), names
  `PAGE_ELEMENT`, placeholders `{text}` are replaced in interactions with `Format String`.
- **Interactions:** the only place with library keywords. Variants (Browser/Selenium, Requests/RESTinstance)
  offer the same names and return values.
- **Tasks / assertions:** imperative business names with arguments. Tests are keyword-driven: each line is a
  task or an assertion.
- **Marking:** keywords that do not belong in tests are recognisable at a glance: interaction files have
  `Keyword Tags    interaction`. `robot:private` does not fit a whole layer (warns on every call from another
  file). Task and assertion names never equal library keyword names.
- Rules: `[Documentation]` for every keyword; assignment without `=`; `VAR`; no `Sleep`, no `Evaluate`.

## §7 robot.toml

Profiles `dev`, `test`, `prod` (set `ENV`), `smoke`, `check` (dry run including excluded tests), `headed`
(web/accessibility), `ci` (`CI=True`, JUnit), plus, depending on the selection, `desktop`, `mobile`,
`email`, `database`, `sap`. Tests tagged `requires-*` are excluded by default; `run-empty-suite = true`.

## §8 Other files

`.gitignore` (among others `.venv/`, `results/`, `playwright-log.txt`, `data/keys/private_key*`, `.env`,
`node_modules/`), `.vscode/` (RobotCode, Python; GitLab Workflow or GitHub Actions extension matching the CI choice),
`.agents/skills/`, `.gitlab-ci.yml` (jobs `check`, `test`, `test-environment`, `template-check`) or
`.github/workflows/robot.yml` (jobs `check`, `test`, `template-check`; profiles only), `data/keys/`,
`data/reference/` (DocTest).

## §8a Maintenance

- If stored answers change meaning in a later version, a Copier migration (`_migrations`) rewrites them on
  `copier update`; it is idempotent and not bound to a version tag (the `rf-*` branches have none).
- Generated pipelines contain the job `template-check` (GitLab `allow_failure: true`, GitHub `continue-on-error`; default branch only):
  it compares `_commit` with the head of `rf-<rf_version>` via `git ls-remote` and lists the available
  version branches.
- The template repository runs the fast tests on every push and pull request (GitHub Actions). A weekly
  workflow reports new Robot Framework releases as an issue.

## §9 READMEs

Template documentation in English and German, switchable at the top of every page: a short start page
(`README.md` / `README.de.md`: what it is, requirements, quick start, links) and topic pages in `docs/` -
getting started (creating a project, dialog, without dialog, troubleshooting), generated projects (structure,
keyword marking, Agent Skills, more libraries) and versions and updates (Robot Framework versions, updates, own
copy as source, staying up to date). Project README (for business teams): quick start (already set up), libraries with documentation links, VS Code, structure, profiles,
environments and credentials, results, first own test, adding libraries (incl. own library), notes per
library, CI, errors, glossary, learning, updating with the version branch - only for selected areas.

## §10 Agent Skills

Every project gets three skills in `.agents/skills/` in the open Agent Skills format (folder with `SKILL.md`,
front matter `name` and `description`):

| Skill | Content |
|---|---|
| `robot-project` | selected libraries with documentation links, own libraries to be added, Screenplay structure, commands, rules (no passwords, no real personal data, no weakening of tests) |
| `robot-write-test` | from test idea to keyword-driven test, why keyword-driven, rules, existing tasks and assertions |
| `robot-explain-results` | running tests, result files, classifying failures (application, test, environment) |

Follow-up questions are kept to a minimum: the assistant looks up missing information in the project, makes
sensible assumptions and states them; it only asks when the result would otherwise be wrong (at most one
question). No internal or personal data, tool-neutral. The project README explains how to use the skills.

## §11 Tests of the template

| Marker | Checks |
|---|---|
| (none) | bilingual dialog, multi-select, "other" and "back" choices, files per option, no Jinja leftovers, Screenplay rules, packages, profiles, Agent Skills |
| `slow` | generate two full projects (Playwright/Requests, Selenium/RESTinstance) with setup, Robocop, all default tests |
| `matrix` | every option alone, everything selected in four variants, 40 fixed random combinations - each with check, Robocop and run |

All tests render the working copy (`vcs_ref="HEAD"`), not the latest tag.

## §12 Open points

| Point | Status |
|---|---|
| Publication (internal GitLab or public) | **[open]** |
| GitLab CI and GitHub Actions with Browser/Selenium in generated projects | untested |
| PostgreSQL and MySQL connection via DatabaseLibrary | untested (no server) |

## History

| Version | Date | Change |
|---|---|---|
| 1.0 | 2026-11-11 | first release (details in the CHANGELOG) |
