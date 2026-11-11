# Versions and updates

**English** | [Deutsch](versions-and-updates.de.md)

[← back to the README](../README.md)

## Robot Framework versions

Every project uses **one fixed Robot Framework version**. The template keeps one branch per version, so older
projects can stay on their version while new projects use a newer one:

| Branch | Robot Framework | Use for |
|--------|-----------------|---------|
| `master` | newest supported version (same as the newest `rf-*` branch) | new projects (default) |
| `rf-7.5.1` | 7.5.1 | projects on 7.5.1 |
| `rf-7.4.2` | 7.4.2 | projects on 7.4.2 |

The version is **never raised automatically**. A weekly workflow only reports new releases (see
[Staying up to date](#staying-up-to-date)); moving to a new version is a deliberate step.

```bash
# new project with a specific version
uvx copier copy --trust --vcs-ref rf-7.4.2 https://github.com/FloJoch/robotframework-copiertemplates .

# update a project and stay on its version
uvx copier update --trust --vcs-ref rf-7.4.2

# move a project to a newer version
uvx copier update --trust --vcs-ref rf-7.5.1
```

> **Always pass `--vcs-ref` when updating a project.** Without it, Copier takes the highest version tag of the
> template - which is on `master` and therefore raises the project to the newest Robot Framework version.
> The README of every generated project shows the right command for its version.

The version is defined in **exactly one place** per branch: `rf_version` in `copier.yml`. All project files
(`pyproject.toml`, README, Agent Skills, CI comment) read it from there. The matching **Python version** is set
the same way per branch (`python_version` in `copier.yml`, used for `.python-version` and `pyproject.toml`). It
is not simply the newest Python: libraries often support a new Python later than Robot Framework, so it is
raised only after the real tests pass. All other libraries are not pinned;
uv resolves versions that match the Robot Framework version, and `uv.lock` in each project freezes them.

### Adding a new Robot Framework version (maintainers)

```bash
# 1. on master: change rf_version in copier.yml (and the version in _message_before_copy, a test checks both),
#    and python_version if the weekly check reports a newer supported Python
uv run pytest -m "not slow and not matrix"
uv run pytest -m slow                   # real projects with the new version
uv run pytest -m matrix                 # optional, about 20 min
# 2. update CHANGELOG.md and README (branch table), commit, tag and create the version branch
git commit -am "Robot Framework 7.6.0"
git tag v1.1.0+rf7.6.0
git branch rf-7.6.0
git push origin master rf-7.6.0 --tags
```

The branch of the previous version stays as it is. Template fixes that should also reach older versions are
cherry-picked onto their `rf-*` branches and tagged there (e.g. `v1.1.1+rf7.4.2`). Whenever `master` changes
later, the branch of its version is moved along: `git push origin master:rf-7.6.0`.

### How a project knows where it comes from

When creating a project, Copier writes `.copier-answers.yml`, for example:

```yaml
_commit: v1.0.0+rf7.5.1                                               # template version at creation / last update
_src_path: https://github.com/FloJoch/robotframework-copiertemplates  # template location
language: en
test_areas: [web, api]
web_library: browser
# ... all other answers from the dialog
```

- `_src_path` is the source for every later update. A local path must be absolute - relative paths such as
  `./template` do not work for updates.
- `_commit` is the Git tag (or commit) of the template the project was last generated from.
- Computed values (for example `rf_version`) are **not** stored - they come from the template version used for
  the update, which is why `--vcs-ref` decides the Robot Framework version.

### What `copier update` does

1. Copier loads the template from `_src_path` at the given `--vcs-ref` (without it: the highest Git tag).
2. It renders the project twice in the background: from the old version (`_commit`) and from the new one,
   each with your stored answers.
3. It applies the **difference** between old and new to your project, like a patch.
   - Files you did not change are simply updated.
   - Your own files (own tests, keywords, pages) stay untouched.
   - If you changed a line that the template changed as well, you get a **conflict** with markers:

     ```text
     <<<<<<< before updating
         "robotframework==7.4.2",
     =======
         "robotframework==7.5.1",
     >>>>>>> after updating
     ```

4. New questions of the template are asked (old answers are kept), the setup steps (`uv sync` etc.) run again
   and `_commit` is set to the new version.

Prerequisites: the project is a **Git repository without uncommitted changes**, and the template is in Git
(URL or absolute path). In the project afterwards:

```bash
git diff                       # look at the changes
uv lock --upgrade              # optional: move the other libraries to matching new versions
uv run robotcode robot         # test, then commit
```

### Releases and tags

Copier treats tags as versions ([PEP 440](https://peps.python.org/pep-0440/)) and refuses updates to a lower
version. Every `rf-*` branch therefore gets its **own tag** with the Robot Framework version as suffix, e.g.
`v1.0.0+rf7.4.2` and `v1.0.0+rf7.5.1`. PEP 440 sorts them by that suffix, so moving a project from 7.4.2 to
7.5.1 is an upgrade, and `copier copy` without `--vcs-ref` picks the newest one. Tag every commit that projects
should get - an untagged commit on an `rf-*` branch can make Copier see a wrong version order. Version
numbers: small fix `v1.0.1+rf…`, new feature or new Robot Framework version `v1.1.0+rf…`, incompatible change
`v2.0.0+rf…`.

### Trying it out step by step

The whole version flow can be tried in a throw-away folder:

```bash
# 1. Generate a project on an older version and commit it
mkdir C:/Temp/project && cd C:/Temp/project
uvx copier copy --trust --vcs-ref rf-7.4.2 https://github.com/FloJoch/robotframework-copiertemplates .
git add -A && git commit -m "Start"

# 2. Update while staying on the version, then move to the newer one
uvx copier update --trust --vcs-ref rf-7.4.2     # stays on 7.4.2
uvx copier update --trust --vcs-ref rf-7.5.1     # pyproject.toml, README.md, .agents/skills/ show 7.5.1
git diff
```

To try changes to the template itself before publishing, generate from a local clone with an absolute path
and `--vcs-ref HEAD` (uses the working copy including uncommitted changes).

### When the template moves

If the repository moves (other server, other name), every project needs the new location:

1. In the project, change the `_src_path` line in `.copier-answers.yml` to the new URL and commit.
   (This is the one place where the file may be edited by hand.)
2. After that, `uvx copier update --trust --vcs-ref <branch>` works as usual.

Branches and tags must move along to the new repository (`git push --all && git push --tags`).

### Limits and alternatives

- There is no central control that updates all projects at once - that is the price for independent projects.
- For automatic hints in projects: Renovate or Dependabot (update merge requests for packages), or a CI job that
  warns when `_commit` is older than the latest template tag.
- `--trust` is required because the template runs commands after creating or updating (`uv sync` etc.). Only
  use it with templates you trust.

## Using your own copy as the source

If you want to decide yourself which versions your projects get - and not depend on this repository - run
your own copy of the template, for example on your company GitLab. Your projects then only ever talk to your
copy.

### 1. Create the copy with all branches and tags

```bash
git clone --mirror https://github.com/FloJoch/robotframework-copiertemplates.git
cd robotframework-copiertemplates.git
git push --mirror https://gitlab.example.com/qa/robotframework-copiertemplates.git
```

A fork on GitHub works as well; make sure the `rf-*` branches and the tags are included.

### 2. Use your copy as the source

```bash
uvx copier copy --trust https://gitlab.example.com/qa/robotframework-copiertemplates.git .
uvx copier copy --trust --vcs-ref rf-7.4.2 https://gitlab.example.com/qa/robotframework-copiertemplates.git .
```

Replace the URL in your copy's README so your teams copy the right commands. Projects store the source in
`_src_path` and update from there; existing projects switch by changing `_src_path` in `.copier-answers.yml`
(see [When the template moves](#when-the-template-moves)).

### 3. Manage your own versions

- Change the template as you like, run the tests (`uv run pytest`) and publish with your own tags
  and your own `rf-*` branches. Tags must be valid PEP 440 versions, for example `v1.1.0` or `v1.1.0.post1`
  for your own follow-up of an upstream release; Copier always picks the highest one.
- Nothing reaches your projects unless you push it to your copy.
- The GitHub workflows in `.github/` only run on GitHub. On GitLab, run the tests in your own pipeline or
  locally; the weekly version check can be run by hand with `python .github/scripts/check_versions.py`.

### 4. Take over changes from this repository (optional)

```bash
git remote add upstream https://github.com/FloJoch/robotframework-copiertemplates.git
git fetch upstream --tags
git merge upstream/master              # or: git cherry-pick <commit>, or merge a single upstream/rf-* branch
uv run pytest                          # check, then tag and push to your copy
```

Upstream tags may collide with yours; if you use your own numbering, fetch without tags (`--no-tags`) and tag
the merged state yourself.

## Staying up to date

- Every push to `master` or an `rf-*` branch and every pull request runs the fast tests
  ([.github/workflows/tests.yml](../.github/workflows/tests.yml)).
- Generated pipelines (GitLab CI and GitHub Actions) contain a job `template-check` that shows (as a
  warning, never failing) when the template branch of the project's Robot Framework version has news.
- A weekly GitHub workflow ([.github/workflows/dependency-check.yml](../.github/workflows/dependency-check.yml))
  compares `rf_version` on `master` with the latest Robot Framework release on PyPI - and `python_version` with
  the newest Python that this Robot Framework version supports - and opens an issue when there is something
  newer. It never changes the version itself. The issue also lists the latest versions
  of all libraries the template installs. It can also be started by hand under
  *Actions > Dependency check > Run workflow*.
- Dependabot ([.github/dependabot.yml](../.github/dependabot.yml)) opens pull requests for the development
  dependencies of this repository and for GitHub Actions.
- In a generated project, `uv tree --outdated --depth 1` shows newer library versions and `uv lock --upgrade`
  applies them (see the project README).
