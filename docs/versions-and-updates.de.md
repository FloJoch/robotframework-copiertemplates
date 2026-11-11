# Versionen und Updates

[English](versions-and-updates.md) | **Deutsch**

[← zurück zur README](../README.de.md)

## Robot-Framework-Versionen

Jedes Projekt nutzt **eine feste Robot-Framework-Version**. Die Vorlage hat je Version einen Branch, damit ältere
Projekte auf ihrer Version bleiben können, während neue Projekte eine neuere nutzen:

| Branch | Robot Framework | Wofür |
|--------|-----------------|-------|
| `master` | neueste unterstützte Version (entspricht dem neuesten `rf-*`-Branch) | neue Projekte (Standard) |
| `rf-7.5.1` | 7.5.1 | Projekte mit 7.5.1 |
| `rf-7.4.2` | 7.4.2 | Projekte mit 7.4.2 |

Die Version wird **nie automatisch angehoben**. Ein wöchentlicher Workflow meldet nur neue Releases (siehe
[Auf dem Laufenden bleiben](#auf-dem-laufenden-bleiben)); der Wechsel auf eine neue Version ist ein bewusster
Schritt.

```bash
# neues Projekt mit einer bestimmten Version
uvx copier copy --trust --vcs-ref rf-7.4.2 https://github.com/FloJoch/robotframework-copiertemplates .

# Projekt aktualisieren und auf seiner Version bleiben
uvx copier update --trust --vcs-ref rf-7.4.2

# Projekt auf eine neuere Version heben
uvx copier update --trust --vcs-ref rf-7.5.1
```

> **Beim Aktualisieren immer `--vcs-ref` angeben.** Ohne diese Angabe nimmt Copier den höchsten Versions-Tag der
> Vorlage - der liegt auf `master` und hebt das Projekt damit auf die neueste Robot-Framework-Version.
> Die README jedes erzeugten Projekts zeigt den passenden Befehl für seine Version.

Die Version steht je Branch an **genau einer Stelle**: `rf_version` in `copier.yml`. Alle Projektdateien
(`pyproject.toml`, README, Agent Skills, CI-Kommentar) lesen sie von dort. Die passende **Python-Version** steht
genauso je Branch fest (`python_version` in `copier.yml`, genutzt für `.python-version` und `pyproject.toml`). Sie
ist nicht einfach die neueste Python-Version: Bibliotheken unterstützen ein neues Python oft später als Robot
Framework, deshalb wird sie erst nach erfolgreichen echten Tests angehoben. Alle anderen Bibliotheken sind nicht
festgelegt; uv wählt passende Versionen zur Robot-Framework-Version, und `uv.lock` im Projekt friert sie ein.

### Neue Robot-Framework-Version aufnehmen (Pflege der Vorlage)

```bash
# 1. auf master: rf_version in copier.yml ändern (und die Version in _message_before_copy, ein Test prüft beide),
#    sowie python_version, wenn die wöchentliche Prüfung ein neueres unterstütztes Python meldet
uv run pytest -m "not slow and not matrix"
uv run pytest -m slow                   # echte Projekte mit der neuen Version
uv run pytest -m matrix                 # optional, ca. 20 Min.
# 2. CHANGELOG.md und README (Branch-Tabelle) ergänzen, committen, taggen und den Versions-Branch anlegen
git commit -am "Robot Framework 7.6.0"
git tag v1.1.0+rf7.6.0
git branch rf-7.6.0
git push origin master rf-7.6.0 --tags
```

Der Branch der vorherigen Version bleibt, wie er ist. Korrekturen, die auch ältere Versionen erreichen sollen,
werden per Cherry-Pick auf deren `rf-*`-Branches übernommen und dort getaggt (z. B. `v1.1.1+rf7.4.2`). Ändert sich `master` später, wird der Branch seiner
Version mitgezogen: `git push origin master:rf-7.6.0`.

### Woher ein Projekt weiß, woher es kommt

Beim Anlegen schreibt Copier `.copier-answers.yml` ins Projekt, z. B.:

```yaml
_commit: v1.0.0+rf7.5.1                                               # Stand der Vorlage beim Anlegen / letzten Update
_src_path: https://github.com/FloJoch/robotframework-copiertemplates  # Adresse der Vorlage
language: de
test_areas: [web, api]
web_library: browser
# ... alle weiteren Antworten aus dem Dialog
```

- `_src_path` ist die Quelle für jedes spätere Update. Ein lokaler Pfad muss absolut sein - relative Pfade wie
  `./vorlage` funktionieren beim Update nicht.
- `_commit` ist der Git-Tag (oder Commit) der Vorlage, aus dem das Projekt zuletzt erzeugt wurde.
- Berechnete Werte (z. B. `rf_version`) werden **nicht** gespeichert - sie kommen aus dem Vorlagenstand, auf den
  aktualisiert wird. Deshalb entscheidet `--vcs-ref` über die Robot-Framework-Version.

### Was `copier update` macht

1. Copier lädt die Vorlage von `_src_path` beim angegebenen `--vcs-ref` (ohne: den höchsten Git-Tag).
2. Es erzeugt das Projekt im Hintergrund zweimal: aus dem alten Stand (`_commit`) und aus dem neuen, jeweils mit
   deinen gespeicherten Antworten.
3. Den **Unterschied** zwischen alt und neu wendet es auf dein Projekt an, wie einen Patch.
   - Dateien, die du nicht geändert hast, werden einfach aktualisiert.
   - Eigene Dateien (eigene Tests, Keywords, Seiten) bleiben unberührt.
   - Hast du eine Zeile geändert, die auch die Vorlage geändert hat, entsteht ein **Konflikt** mit Markierungen:

     ```text
     <<<<<<< before updating
         "robotframework==7.4.2",
     =======
         "robotframework==7.5.1",
     >>>>>>> after updating
     ```

4. Neue Fragen der Vorlage werden gestellt (alte Antworten bleiben), die Einrichtungsschritte (`uv sync` usw.)
   laufen erneut, und `_commit` wird auf den neuen Stand gesetzt.

Voraussetzungen: Das Projekt ist ein **Git-Repository ohne offene Änderungen**, und die Vorlage liegt in Git
(Adresse oder absoluter Pfad). Danach im Projekt:

```bash
git diff                       # Änderungen ansehen
uv lock --upgrade              # optional: übrige Bibliotheken auf passende neue Versionen heben
uv run robotcode robot         # testen, dann committen
```

### Releases und Tags

Copier versteht Tags als Versionen ([PEP 440](https://peps.python.org/pep-0440/)) und lehnt Updates auf eine
niedrigere Version ab. Jeder `rf-*`-Branch bekommt deshalb einen **eigenen Tag** mit der Robot-Framework-Version
als Zusatz, z. B. `v1.0.0+rf7.4.2` und `v1.0.0+rf7.5.1`. PEP 440 sortiert nach diesem Zusatz, der Wechsel eines
Projekts von 7.4.2 auf 7.5.1 ist also ein Upgrade, und `copier copy` ohne `--vcs-ref` nimmt den neuesten. Jeden
Commit taggen, den Projekte bekommen sollen - ein ungetaggter Commit auf einem `rf-*`-Branch kann bei Copier zu
einer falschen Reihenfolge führen. Versionsnummern: kleine Korrektur `v1.0.1+rf…`, neue Funktion oder neue
Robot-Framework-Version `v1.1.0+rf…`, inkompatible Änderung `v2.0.0+rf…`.

### Schritt für Schritt ausprobieren

Der ganze Versionsablauf lässt sich in einem Wegwerf-Ordner ausprobieren:

```bash
# 1. Projekt mit einer älteren Version erzeugen und committen
mkdir C:/Temp/projekt && cd C:/Temp/projekt
uvx copier copy --trust --vcs-ref rf-7.4.2 https://github.com/FloJoch/robotframework-copiertemplates .
git add -A && git commit -m "Start"

# 2. Aktualisieren und auf der Version bleiben, dann auf die neuere wechseln
uvx copier update --trust --vcs-ref rf-7.4.2     # bleibt auf 7.4.2
uvx copier update --trust --vcs-ref rf-7.5.1     # pyproject.toml, README.md, .agents/skills/ zeigen 7.5.1
git diff
```

Um Änderungen an der Vorlage selbst vor dem Veröffentlichen auszuprobieren, aus einem lokalen Klon mit
absolutem Pfad und `--vcs-ref HEAD` erzeugen (nutzt die Arbeitskopie einschließlich nicht committeter
Änderungen).

### Wenn die Vorlage umzieht

Zieht das Repository um (anderer Server, anderer Name), braucht jedes Projekt die neue Adresse:

1. Im Projekt in `.copier-answers.yml` die Zeile `_src_path` auf die neue Adresse ändern und committen.
   (Das ist die eine Stelle, an der diese Datei von Hand geändert werden darf.)
2. Danach funktioniert `uvx copier update --trust --vcs-ref <branch>` wie gewohnt.

Branches und Tags müssen ins neue Repository mitziehen (`git push --all && git push --tags`).

### Grenzen und Alternativen

- Es gibt keine zentrale Steuerung, die alle Projekte auf einmal aktualisiert - das ist der Preis für
  unabhängige Projekte.
- Für automatische Hinweise in Projekten: Renovate oder Dependabot (Update-Merge-Requests für Pakete) oder ein
  CI-Job, der warnt, wenn `_commit` älter als der neueste Tag der Vorlage ist.
- `--trust` ist nötig, weil die Vorlage nach dem Anlegen oder Aktualisieren Befehle ausführt (`uv sync` usw.).
  Nur bei Vorlagen verwenden, denen man vertraut.

## Eigene Kopie als Quelle nutzen

Wer selbst entscheiden will, welche Versionen die eigenen Projekte bekommen - und nicht von diesem Repository
abhängen möchte -, betreibt eine eigene Kopie der Vorlage, z. B. im Firmen-GitLab. Die Projekte sprechen dann
nur noch mit dieser Kopie.

### 1. Kopie mit allen Branches und Tags anlegen

```bash
git clone --mirror https://github.com/FloJoch/robotframework-copiertemplates.git
cd robotframework-copiertemplates.git
git push --mirror https://gitlab.example.com/qa/robotframework-copiertemplates.git
```

Ein Fork auf GitHub geht genauso; wichtig ist, dass die `rf-*`-Branches und die Tags mitkommen.

### 2. Die Kopie als Quelle verwenden

```bash
uvx copier copy --trust https://gitlab.example.com/qa/robotframework-copiertemplates.git .
uvx copier copy --trust --vcs-ref rf-7.4.2 https://gitlab.example.com/qa/robotframework-copiertemplates.git .
```

Die Adresse in der README deiner Kopie anpassen, damit deine Teams die richtigen Befehle kopieren. Projekte
speichern die Quelle in `_src_path` und aktualisieren von dort; bestehende Projekte wechseln, indem sie
`_src_path` in `.copier-answers.yml` ändern (siehe [Wenn die Vorlage umzieht](#wenn-die-vorlage-umzieht)).

### 3. Eigene Versionen verwalten

- Die Vorlage nach Bedarf ändern, die Tests ausführen (`uv run pytest`) und mit eigenen Tags und eigenen
  `rf-*`-Branches veröffentlichen. Tags müssen gültige PEP-440-Versionen sein, z. B. `v1.1.0` oder
  `v1.1.0.post1` für eine eigene Folgeversion eines Upstream-Releases; Copier nimmt immer die höchste.
- Bei deinen Projekten kommt nur an, was du in deine Kopie pushst.
- Die GitHub-Workflows in `.github/` laufen nur auf GitHub. In GitLab die Tests in einer eigenen Pipeline oder
  lokal ausführen; die wöchentliche Versionsprüfung lässt sich von Hand starten:
  `python .github/scripts/check_versions.py`.

### 4. Änderungen aus diesem Repository übernehmen (optional)

```bash
git remote add upstream https://github.com/FloJoch/robotframework-copiertemplates.git
git fetch upstream --tags
git merge upstream/master              # oder: git cherry-pick <commit>, oder einen einzelnen upstream/rf-*-Branch mergen
uv run pytest                          # prüfen, dann taggen und in die Kopie pushen
```

Upstream-Tags können mit deinen kollidieren; bei eigener Nummerierung ohne Tags holen (`--no-tags`) und den
gemergten Stand selbst taggen.

## Auf dem Laufenden bleiben

- Jeder Push auf `master` oder einen `rf-*`-Branch und jeder Pull Request führt die schnellen Tests aus
  ([.github/workflows/tests.yml](../.github/workflows/tests.yml)).
- Erzeugte Pipelines (GitLab CI und GitHub Actions) enthalten einen Job `template-check`, der (als Warnung, nie
  als Fehler) zeigt, wenn der Vorlagen-Branch der Robot-Framework-Version des Projekts Neues hat.
- Ein wöchentlicher GitHub-Workflow ([.github/workflows/dependency-check.yml](../.github/workflows/dependency-check.yml))
  vergleicht `rf_version` auf `master` mit dem neuesten Robot-Framework-Release auf PyPI - und `python_version`
  mit dem neuesten Python, das diese Robot-Framework-Version unterstützt - und legt bei Neuem ein Issue an. Er ändert die Version nie selbst. Das Issue listet auch die neuesten Versionen aller
  Bibliotheken, die die Vorlage installiert. Von Hand starten: *Actions > Dependency check > Run workflow*.
- Dependabot ([.github/dependabot.yml](../.github/dependabot.yml)) öffnet Pull Requests für die
  Entwicklungsabhängigkeiten dieses Repositorys und für GitHub Actions.
- In einem erzeugten Projekt zeigt `uv tree --outdated --depth 1` neuere Bibliotheksversionen, `uv lock --upgrade`
  übernimmt sie (siehe Projekt-README).
