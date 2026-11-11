# Changelog

Changes to the template. Every Robot Framework version has a branch `rf-<version>` with its own release tags
(`v<version>+rf<rf_version>`, e.g. `v1.0.0+rf7.4.2`) (see [docs/versions-and-updates.md](docs/versions-and-updates.md)).

## 1.0.0 (2026-11-12)

First release. `master` and `rf-7.5.1` use Robot Framework 7.5.1, `rf-7.4.2` uses Robot Framework 7.4.2.

### Dialog

- English or German. All areas in **one** multi-select list, grouped into basic (web, API) and extended
  (e-mail, database, test data, PDF/images, accessibility, desktop, mobile, SAP); Space toggles, Enter confirms.
- A library question only where there is a choice: web (Browser Library or SeleniumLibrary), API
  (RequestsLibrary or RESTinstance) and database (SQLite, PostgreSQL, MySQL/MariaDB), each with
  **"Other / own library"** and "↩ Back". For an own library no example files are generated; the final
  message, the project README and the `robot-project` skill explain how to add it.
- CI pipeline: GitLab CI, GitHub Actions or none.
- The command runs in the project folder (`copier copy … .`); the files go straight into it, the project name
  defaults to the folder name.
- A short coloured overview before the dialog (at most 10 lines, because Copier captures the mouse wheel while
  the dialog runs) and a final message with next steps, the Agent Skills and how to add libraries.

### Generated projects

- Completely English: keywords, test names, documentation, comments, file names, README and skills.
- **Keyword-driven tests in the Screenplay structure** in `resources/`: `main.resource` (standard libraries,
  CryptoLibrary, URLs and credentials per environment, global values), abilities without keywords, page
  objects per page, interactions, tasks and generic assertions. Interactions carry `Keyword Tags    interaction`
  and are never used in tests; task and assertion names never hide library keywords. All imports via
  `${EXECDIR}`.
- **Browser Library only once:** shared browser layer for web and accessibility; Selenium with its own layer
  and the same keyword names.
- **Hello world tests** for every library; tests that need a device, program, mailbox or server are excluded
  by default and run with their profile.
- **Profiles** in `robot.toml` with descriptions (`dev`, `test`, `prod`, `smoke`, `check`, `headed`, `ci` and
  per area), `${BROWSER_SPEED}` for slower browser tests, `${CI}` for pipelines.
- **Project files:** `.gitignore`, `.gitattributes` (LF, so update conflicts only show changed lines), VS Code
  recommendations with the project environment set, `data/keys/` for the CryptoLibrary.
- **Pipelines:** `.gitlab-ci.yml` (image `ppodgorsek/robot-framework`) or `.github/workflows/robot.yml`, each
  with the jobs `check`, `test` and `template-check` (hint, never failing, when the template branch of the
  project's Robot Framework version has news).
- **Agent Skills** in `.agents/skills/` (open format, tool-neutral): `robot-project`, `robot-write-test`
  (keyword-driven tests instead of Given/When/Then), `robot-explain-results` - tailored to the selected
  libraries, no internal data, follow-up questions kept to a minimum.
- The project README explains how to find (`uv tree --outdated --depth 1`) and apply (`uv lock --upgrade`)
  newer library versions and how to add libraries (`uv add <package>` - package names differ per library).

### Versions and maintenance

- Robot Framework and Python are pinned in one place per branch (`rf_version`, `python_version` in
  `copier.yml`); one branch `rf-<version>` per Robot Framework version, never raised automatically. Projects update with `copier update --vcs-ref rf-<version>`.
- GitHub Actions: fast tests on every push and pull request; a weekly workflow reports new Robot Framework
  releases and newer Python versions supported by Robot Framework as an issue (with the latest versions of all
  libraries); Dependabot for the development
  dependencies.
- Documentation in English and German: a short README with quick start (`README.md`, `README.de.md`) and
  topic pages in `docs/` (getting started, generated projects, versions and updates) - including own copy as
  template source, further libraries and tools (checked on PyPI), keyword marking and links to MarketSquare.

### Researched and checked

Windows 11, Python 3.13, Robot Framework 7.4.2 and 7.5.1:

- RESTinstance 1.8.0 runs on Python 3.13 (its dependency `flex` emits harmless SyntaxWarnings); `GET`/`POST`
  return the response as a dictionary with `status` and `body`.
- ImapLibrary2, DatabaseLibrary with `psycopg2-binary` and `pymysql`, DocTestLibrary (image and PDF),
  FakerLibrary and CryptoLibrary install and run. Connections to real database servers and mailboxes are
  untested (no server available), as are Appium and SAP.
- PlatynUI: `Type Keys` needs window focus; a click into the display reliably gets it.
- Copier (9.3 and newer) supports multi-select (`multiselect: true`); entries cannot be coloured, Enter
  confirms. The controls are therefore shown in colour in the overview before the dialog.
- Copier renders help texts and choice labels with Jinja (bilingual dialog); computed values are not yet
  available in the intro text, so the version is repeated there (a test checks both match).
- `copier update` tried: change the version, update a project; own files are kept, conflicts only affect the
  changed line. A relative `_src_path` does not work for updates.
- `robot:private` is not suitable for marking a whole layer: Robot Framework warns whenever a private keyword
  is called from another file. Interactions use the tag `interaction` instead.
- Long conditions in file names make paths too long on Windows; conditions are therefore computed variables
  (`use_browser`, `use_selenium`, `use_pages`, `use_db_server`) in `copier.yml`.
- The Microsoft Store Python redirects writes to `AppData`, which breaks Copier's Git cache. Fix:
  `uv python install 3.13` (docs/getting-started.md, "Troubleshooting").
- Further libraries for the documentation checked on PyPI (latest release, Robot Framework requirement). Not
  included: Robotidy (now part of Robocop), ExcelLibrary/ExcelLib, CSV, JSON schema and OTP libraries
  (unmaintained for years), Kafka/MQTT/RPA Framework (special cases).
- GitLab CI and GitHub Actions in generated projects have not been run on a server yet.
