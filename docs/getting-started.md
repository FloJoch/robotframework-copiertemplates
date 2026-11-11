# Getting started

**English** | [Deutsch](getting-started.de.md)

[← back to the README](../README.md)

## Create a project

Run the command **inside the project folder** (e.g. a freshly cloned, empty repository) - the files go
straight into it:

```bash
cd my-project
uvx copier copy --trust https://github.com/FloJoch/robotframework-copiertemplates .
```

- For an older Robot Framework version add its branch, e.g. `--vcs-ref rf-7.4.2`
  (see [Robot Framework versions](versions-and-updates.md#robot-framework-versions)).
- Existing files with the same name (e.g. a `README.md`) are only overwritten after asking.
- `--trust` lets the template set up the project afterwards: `git init`, `uv sync` (Python environment
  `.venv`), `rfbrowser init chromium` for the Browser Library, `npm install` for accessibility and a syntax
  check of all tests.

## The dialog

```text
🌐 Sprache für den Dialog / Language for this dialog        › English
📁 Project name? (Enter keeps the folder name)              customer-portal-tests
🧪 What do you want to test? (Space: select, Enter: confirm)
   ● Basic    · 🌍 Web            - open pages in a browser, check texts
   ● Basic    · 🔌 API            - call REST interfaces, check responses
   ○ Extended · 📧 E-mail         - wait for and read e-mails (ImapLibrary2)
   ○ Extended · 💾 Database       - read and check data with SQL
   ● Extended · 🎲 Test data      - names, addresses, e-mails (FakerLibrary)
   ○ Extended · 📄 PDF and images - check and compare (DocTestLibrary)
   ○ Extended · 🔍 Accessibility  - axe-core, HTML report per page
   ○ Extended · 💻 Desktop        - Windows applications (PlatynUI)
   ○ Extended · 📱 Mobile         - Android apps (AppiumLibrary)
   ○ Extended · 🏢 SAP GUI        - Windows (RoboSAPiens)
🌍 Web: which browser library?                              › Browser Library (Playwright)
                                                              SeleniumLibrary (Selenium)
                                                              Other / own library - none of these, I add my own
                                                              ↩ Back - no web tests after all
🔌 API: which library?                                      › RequestsLibrary
🚀 Create a CI pipeline?                                     › GitLab CI
                                                              GitHub Actions
                                                              None
```

**Arrow keys** move, **Space** ticks, **Enter** confirms, **Ctrl+C** cancels. Only web, API and database ask
for the library. "Other / own library" creates no example files for that area; the project README explains
how to add yours. Every selected area gets runnable example tests.

Afterwards:

```bash
code .                      # open VS Code, install the recommended extensions
uv run robotcode robot      # run the example tests, then open results/report.html
```

## Without the dialog (for example in CI)

```bash
uvx copier copy --trust --defaults --data-file answers.yml https://github.com/FloJoch/robotframework-copiertemplates .
```

```yaml
language: en
project_name: "Customer Portal Tests"     # omit = name of the target folder
test_areas: [web, api, database, faker]   # web, api, email, database, faker, doctest, accessibility, desktop, mobile, sap
web_library: browser          # browser, selenium, other or none
api_library: requests         # requests, restinstance, other or none
database_driver: postgresql   # sqlite, postgresql, mysql, other or none
ci_provider: gitlab           # gitlab, github or none
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Setup did not run | `--trust` was missing. Run `uv sync` in the project folder, for the Browser Library also `uv run rfbrowser init chromium`. |
| `fatal: not a git repository: …\copier\Cache\git\…` (Windows) | uv picked the Python from the Microsoft Store. Run `uv python install` once and repeat the command. |
| `rfbrowser init` fails | Install Node.js, set a proxy if needed (`HTTPS_PROXY`), then `uv run rfbrowser init chromium`. |
| `uv` cannot reach pypi.org | Set an internal package mirror via `UV_INDEX_URL`. |
| Mouse wheel does not scroll during the dialog | Copier uses it for the lists while the dialog runs - use the arrow keys. |

More about updating projects: [Versions and updates](versions-and-updates.md).
