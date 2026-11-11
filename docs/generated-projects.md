# Generated projects

**English** | [Deutsch](generated-projects.de.md)

[← back to the README](../README.md)

## Structure of generated projects

The tests are **keyword-driven** and follow the **Screenplay pattern** (without actor). A test case is a
sequence of business keywords with arguments - each line is either an action (task) or a check (assertion):

```robotframework
Product Lands In The Cart
    Open Login Page
    Log In
    Add Product To Cart    sauce-labs-backpack
    Element Should Show Text    ${MAIN_CART_BADGE}    1
```

The test reads like the specification and is exactly what runs. Keywords are reused across tests, test data
is visible as arguments, and acting and checking stay separate. Everything except the tests lives in
`resources/`; all imports start with `${EXECDIR}` (the project folder).

| Layer | Content | Used in tests |
|-------|---------|---------------|
| `resources/main.resource` | standard libraries, CryptoLibrary, URLs and credentials per environment (dev, test, prod), global values such as `${CI}`, `${BROWSER}`, `${BROWSER_SPEED}`, `${TIMEOUT}` | - |
| `resources/abilities/` | one file per library: `Library` import and settings (for example mail server, database connection), **no keywords** | - |
| `resources/pages/` | page objects, one file per page: `login_page`, `main_page`, `cart_page`, `settings_page` - selectors via `id` or `data-test` | selectors only |
| `resources/interactions/` | technical helper keywords - the only place that uses library keywords; tagged `interaction` | no |
| `resources/tasks/` | business actions with arguments, for example `Add Product To Cart    sauce-labs-backpack`; also setup and teardown such as `Start Browser` | yes |
| `resources/assertions/` | **generic** checks, for example `Element Should Show Text    ${MAIN_TITLE}    Products` | yes |
| `tests/<area>/` | test cases built from tasks and assertions | - |

Web tests with the Browser Library and the accessibility checks share one browser layer
(`browser_ability`, `browser_interactions`) - the Browser Library is imported only once.

### Recommendation: mark keywords that do not belong in tests

Tests are meant to be read by business people with little technical background. It helps to make keywords
that should **not** appear in a test recognisable at a glance, so nobody uses them there by accident. Common
ways are:

- a **tag** on the technical keywords, for example `Keyword Tags    interaction` in the settings of a file -
  visible in RobotCode, in the log and in the keyword documentation,
- a **prefix** such as a leading underscore (`_Click When Ready`),
- a **different language** for technical keywords than for business keywords.

The generated projects use the tag: every file in `resources/interactions/` has `Keyword Tags    interaction`,
and a test of this template checks that tests never call these keywords. Note: the built-in tag
`robot:private` does not fit a whole layer - Robot Framework warns whenever a private keyword is used from
another file, and tasks always call interactions from another file. Pick the convention that fits your team -
the point is that a test only contains readable business steps.

### Simpler structure for small projects

The Screenplay layers pay off when many people write tests over a longer time. For a small project or a first
try they can feel like too much. Then simply merge them into a basic structure:

```text
tests/<area>/                       test cases
resources/keywords/<area>.resource  your keywords: library import, actions and checks in one file
resources/pages/                    selectors per page (keep these - they make tests robust)
resources/main.resource             standard libraries, environments, credentials
```

How to get there from a generated project:

1. Per area, create `resources/keywords/<area>.resource` with `Resource    ${EXECDIR}/resources/main.resource`,
   the `Library` line from the ability and the needed `Resource` lines for pages.
2. Move the keywords of `tasks/`, `assertions/` and `interactions/` of that area into it (or keep only the
   ones you need and call library keywords directly).
3. Let the tests import `resources/keywords/<area>.resource` instead of tasks and assertions, then delete
   the folders `abilities/`, `interactions/`, `tasks/` and `assertions/`.
4. Check with `uv run robotcode -p check robot` and `uv run robocop check`.

The tests stay keyword-driven - only the layers behind them are fewer. Keep in mind that `copier update` then
reports conflicts for the moved files; for a simplified project it is usually easier not to update from the
template anymore. The rule that matters most stays the same: tests contain readable business steps, technical
details live in keywords and pages.

Other structures work just as well - the layers of this template are a suggestion, not a requirement.
Common variants are, for example:

- **by feature or business area:** `resources/<feature>/` with keywords and pages of that feature together,
- **page objects only:** one resource file per page with its selectors *and* keywords,
- **by test level:** separate folders for API, UI and end-to-end tests with shared keywords in `resources/common/`.

Whatever you choose, keep these points: tests contain readable business steps, selectors live in one place,
imports start from `${EXECDIR}`, and execution options stay in the profiles of `robot.toml`.

## Agent Skills

Every project contains three skills in `.agents/skills/` in the open [Agent Skills](https://agentskills.io/)
format (one `SKILL.md` per folder), tailored to the selected libraries:

| Skill | Purpose |
|-------|---------|
| `robot-project` | structure, installed libraries with documentation links, commands, rules |
| `robot-write-test` | turn a test idea into a keyword-driven test using the existing tasks and assertions |
| `robot-explain-results` | run tests and explain failures (application, test or environment) |

**Usage:** open the project folder in a coding assistant that supports Agent Skills - many tools pick up
`.agents/skills/` automatically. If a tool expects a different folder, copy the skill folders there. Without
skill support - for example in a plain chat - paste the content of one or all `SKILL.md` files as an
instruction or system prompt: every skill is self-contained (structure, rules, existing keywords), asks for a
file only when it really needs it and answers with copyable file blocks. The skills keep follow-up questions
to a minimum and contain **no internal or personal data**. Step by step for a web chat: see below;
details are also in the README of each generated project, section "Coding assistants (Agent Skills)".

### Using the skills in a web chat

Works with any chat assistant in the browser, also without file access:

1. Open the generated project and the file of the skill you need, e.g.
   `.agents/skills/robot-write-test/SKILL.md` - the files are plain text with the project's real details.
2. Copy the **whole** content (including the part between `---` at the top).
3. Paste it in the chat - as **custom instructions / system prompt / project knowledge** if the chat offers
   that, otherwise as the **first message** with a line like "Use these instructions for this conversation."
   For general help paste all three skills, one after another.
4. Ask your question, e.g. "Write a test: login with a wrong password shows an error message" or paste a
   failure message from `results/log.html` and ask "Why did this test fail?".
5. If the assistant asks for a file, paste just that file (e.g. a page object). It answers with complete
   blocks per file path - copy them into the project and run the commands it names.

Do not paste credentials, tokens or real personal data. Paste the skills again after adding keywords or
libraries, so the chat knows the current state (or add a short note what changed).

## More libraries and tools worth a look

The dialog deliberately covers only the most common areas. When a project grows, these well-known additions
are a good next step - each is added with `uv add <package>` and, for libraries, an ability and interactions
as described in the project README ("Adding more libraries"). Package names differ - check the exact name
on PyPI. These packages are not part of the template's tests.

| Need | Package | Note |
|------|---------|------|
| Run tests in parallel | [`robotframework-pabot`](https://pypi.org/project/robotframework-pabot/) | Shortens long test runs; tests must be independent (they already are in this template). |
| Data-driven tests from CSV or Excel | [`robotframework-datadriver`](https://pypi.org/project/robotframework-datadriver/) | One test template, many data rows maintained by the business side. |
| Excel files | [`robotframework-excelsage`](https://pypi.org/project/robotframework-excelsage/) | Check exports and imports. |
| Servers and files via SSH/SFTP | [`robotframework-sshlibrary`](https://pypi.org/project/robotframework-sshlibrary/) | Run commands, transfer files, check batch jobs. |
| Results over time | [`robotframework-dashboard`](https://pypi.org/project/robotframework-dashboard/) | HTML dashboard across many test runs. |
| API tests from an OpenAPI specification | [`robotframework-openapidriver`](https://pypi.org/project/robotframework-openapidriver/) | Generates test cases from the spec; for teams that already maintain OpenAPI files. |
| Re-run failed tests | [`robotframework-retryfailed`](https://pypi.org/project/robotframework-retryfailed/) | Use with care: retries can hide real, intermittent errors. |

Formatting is already included: `uv run robocop format` (the former Robotidy is part of Robocop now).

For everything else, look at [MarketSquare](https://github.com/MarketSquare), the GitHub organisation of the
Robot Framework community, and the overview at <https://robotframework.org/#resources>. Before adding a
library, check on PyPI that it is still maintained and supports your Robot Framework version.
