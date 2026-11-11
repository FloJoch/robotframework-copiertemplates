# robotframework-copiertemplates

**English** | [Deutsch](README.de.md)

A [Copier](https://copier.readthedocs.io/) template that sets up a ready-to-run
[Robot Framework](https://robotframework.org/) project with **one command**. A short dialog asks what you want
to test; afterwards the project is created, the Python environment is installed and example tests for every
selected library pass right away.

| Area | Library | Group in the dialog |
|------|---------|---------------------|
| Web | Browser Library (Playwright) or SeleniumLibrary | basic |
| API | RequestsLibrary or RESTinstance | basic |
| E-mail | ImapLibrary2 | extended |
| Database | DatabaseLibrary (SQLite, PostgreSQL, MySQL/MariaDB) | extended |
| Test data | FakerLibrary | extended |
| PDF and images | DocTestLibrary | extended |
| Accessibility | axe-core with Browser Library | extended |
| Desktop | PlatynUI | extended |
| Mobile | AppiumLibrary | extended |
| SAP | RoboSAPiens | extended |

Always included: Robot Framework in a fixed version, CryptoLibrary, Robocop, RobotCode, VS Code recommendations and Agent Skills for coding assistants.
Optional: a pipeline for GitLab CI or GitHub Actions. Generated projects are in English; the dialog speaks
English and German.

## Requirements

[uv](https://docs.astral.sh/uv/getting-started/installation/) and [Git](https://git-scm.com/downloads) - uv also
installs the Python version that matches the Robot Framework version. For the Browser Library, accessibility and mobile also
[Node.js (LTS)](https://nodejs.org/); for the SeleniumLibrary Google Chrome. [VS Code](https://code.visualstudio.com/)
is recommended.

## Quick start

Run the command **inside the project folder** - the files go straight into it:

```bash
cd my-project
uvx copier copy --trust https://github.com/FloJoch/robotframework-copiertemplates .
```

Tick the areas in the list (Space), confirm with Enter, pick the library where asked - done. Then:

```bash
code .                      # open VS Code, install the recommended extensions
uv run robotcode robot      # run the example tests, then open results/report.html
```

A specific Robot Framework version (one branch per version):

```bash
uvx copier copy --trust --vcs-ref rf-7.5.1 https://github.com/FloJoch/robotframework-copiertemplates .   # Robot Framework 7.5.1 (newest)
uvx copier copy --trust --vcs-ref rf-7.4.2 https://github.com/FloJoch/robotframework-copiertemplates .   # Robot Framework 7.4.2
```

Update a project later and stay on its version:

```bash
uvx copier update --trust --vcs-ref rf-7.5.1    # or rf-7.4.2
```

## Documentation

| Topic | Contents |
|-------|----------|
| [Getting started](docs/getting-started.md) | creating a project in detail, the dialog, without the dialog, troubleshooting |
| [Generated projects](docs/generated-projects.md) | structure (keyword-driven, Screenplay), keyword marking, Agent Skills, more libraries |
| [Versions and updates](docs/versions-and-updates.md) | Robot Framework versions, `copier update`, your own copy as the source |

Every generated project also has its own README with all details for the selected libraries.
