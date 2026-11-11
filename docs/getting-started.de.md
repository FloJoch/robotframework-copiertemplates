# Erste Schritte

[English](getting-started.md) | **Deutsch**

[← zurück zur README](../README.de.md)

## Projekt anlegen

Den Befehl **im Projektordner** ausführen (z. B. einem frisch geklonten, leeren Repository) - die Dateien kommen
direkt dort hinein:

```bash
cd mein-projekt
uvx copier copy --trust https://github.com/FloJoch/robotframework-copiertemplates .
```

- Für eine ältere Robot-Framework-Version deren Branch angeben, z. B. `--vcs-ref rf-7.4.2`
  (siehe [Robot-Framework-Versionen](versions-and-updates.de.md#robot-framework-versionen)).
- Vorhandene Dateien mit gleichem Namen (z. B. eine `README.md`) werden nur nach Rückfrage überschrieben.
- `--trust` lässt die Vorlage das Projekt danach einrichten: `git init`, `uv sync` (Python-Umgebung `.venv`),
  `rfbrowser init chromium` für die Browser Library, `npm install` für Barrierefreiheit und ein Syntax-Check
  aller Tests.

## Der Dialog

```text
🌐 Sprache für den Dialog / Language for this dialog        › Deutsch
📁 Wie heißt das Projekt? (Enter übernimmt den Ordnernamen) kundenportal-tests
🧪 Was möchtest du testen? (Leertaste: auswählen, Enter: bestätigen)
   ● Basis    · 🌍 Web              - Seiten im Browser öffnen, Texte prüfen
   ● Basis    · 🔌 API              - REST-Schnittstellen aufrufen, Antworten prüfen
   ○ Erweitert· 📧 E-Mail           - auf E-Mails warten und lesen (ImapLibrary2)
   ○ Erweitert· 💾 Datenbank        - Daten per SQL lesen und prüfen
   ● Erweitert· 🎲 Testdaten        - Namen, Adressen, E-Mails (FakerLibrary)
   ○ Erweitert· 📄 PDF und Bilder   - prüfen und vergleichen (DocTestLibrary)
   ○ Erweitert· 🔍 Barrierefreiheit - axe-core, HTML-Bericht je Seite
   ○ Erweitert· 💻 Desktop          - Windows-Anwendungen (PlatynUI)
   ○ Erweitert· 📱 Mobile           - Android-Apps (AppiumLibrary)
   ○ Erweitert· 🏢 SAP GUI          - Windows (RoboSAPiens)
🌍 Web: welche Browser-Bibliothek?                          › Browser Library (Playwright)
                                                              SeleniumLibrary (Selenium)
                                                              Andere / eigene Bibliothek - keine davon, ...
                                                              ↩ Zurück - doch keine Web-Tests
🔌 API: welche Bibliothek?                                  › RequestsLibrary
🚀 CI-Pipeline erzeugen?                                     › GitLab CI
                                                              GitHub Actions
                                                              Keine
```

**Pfeiltasten** bewegen, **Leertaste** kreuzt an, **Enter** bestätigt, **Strg+C** bricht ab. Nur Web, API und
Datenbank fragen nach der Bibliothek. „Andere / eigene Bibliothek“ legt für den Bereich keine Beispieldateien an;
die Projekt-README erklärt, wie du deine einbindest. Jeder gewählte Bereich bekommt lauffähige Beispieltests.

Danach:

```bash
code .                      # VS Code öffnen, empfohlene Erweiterungen installieren
uv run robotcode robot      # Beispieltests ausführen, dann results/report.html öffnen
```

## Ohne Dialog (z. B. in CI)

```bash
uvx copier copy --trust --defaults --data-file antworten.yml https://github.com/FloJoch/robotframework-copiertemplates .
```

```yaml
language: de
project_name: "Kundenportal Tests"        # weglassen = Name des Zielordners
test_areas: [web, api, database, faker]   # web, api, email, database, faker, doctest, accessibility, desktop, mobile, sap
web_library: browser          # browser, selenium, other oder none
api_library: requests         # requests, restinstance, other oder none
database_driver: postgresql   # sqlite, postgresql, mysql, other oder none
ci_provider: gitlab           # gitlab, github oder none
```

## Häufige Probleme

| Problem | Lösung |
|---------|--------|
| Einrichtung ist nicht gelaufen | `--trust` fehlte. Im Projektordner `uv sync` ausführen, für die Browser Library zusätzlich `uv run rfbrowser init chromium`. |
| `fatal: not a git repository: …\copier\Cache\git\…` (Windows) | uv hat das Python aus dem Microsoft Store gewählt. Einmalig `uv python install` ausführen und den Befehl wiederholen. |
| `rfbrowser init` bricht ab | Node.js installieren, ggf. Proxy setzen (`HTTPS_PROXY`), dann `uv run rfbrowser init chromium`. |
| `uv` erreicht pypi.org nicht | Internen Paketspiegel über `UV_INDEX_URL` setzen. |
| Mausrad scrollt während des Dialogs nicht | Copier nutzt es während des Dialogs für die Listen - Pfeiltasten verwenden. |

Mehr zum Aktualisieren von Projekten: [Versionen und Updates](versions-and-updates.de.md).
