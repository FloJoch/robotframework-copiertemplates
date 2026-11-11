# robotframework-copiertemplates

[English](README.md) | **Deutsch**

Eine [Copier](https://copier.readthedocs.io/)-Vorlage, die mit **einem Befehl** ein lauffähiges
[Robot-Framework](https://robotframework.org/)-Projekt einrichtet. Ein kurzer Dialog fragt, was du testen
möchtest; danach ist das Projekt angelegt, die Python-Umgebung installiert und für jede gewählte Bibliothek
laufen Beispieltests sofort grün.

| Bereich | Bibliothek | Gruppe im Dialog |
|---------|------------|------------------|
| Web | Browser Library (Playwright) oder SeleniumLibrary | Basis |
| API | RequestsLibrary oder RESTinstance | Basis |
| E-Mail | ImapLibrary2 | Erweitert |
| Datenbank | DatabaseLibrary (SQLite, PostgreSQL, MySQL/MariaDB) | Erweitert |
| Testdaten | FakerLibrary | Erweitert |
| PDF und Bilder | DocTestLibrary | Erweitert |
| Barrierefreiheit | axe-core mit Browser Library | Erweitert |
| Desktop | PlatynUI | Erweitert |
| Mobile | AppiumLibrary | Erweitert |
| SAP | RoboSAPiens | Erweitert |

Immer dabei: Robot Framework in einer festen Version, CryptoLibrary, Robocop, RobotCode, VS-Code-Empfehlungen und Agent Skills für KI-Assistenten. Optional:
eine Pipeline für GitLab CI oder GitHub Actions. Erzeugte Projekte sind englisch; der Dialog spricht Deutsch und
Englisch.

## Voraussetzungen

[uv](https://docs.astral.sh/uv/getting-started/installation/) und [Git](https://git-scm.com/downloads) - uv
installiert auch die Python-Version, die zur Robot-Framework-Version passt. Für Browser Library, Barrierefreiheit und Mobile zusätzlich
[Node.js (LTS)](https://nodejs.org/), für die SeleniumLibrary Google Chrome. [VS Code](https://code.visualstudio.com/)
wird empfohlen.

## Schnellstart

Den Befehl **im Projektordner** ausführen - die Dateien kommen direkt dort hinein:

```bash
cd mein-projekt
uvx copier copy --trust https://github.com/FloJoch/robotframework-copiertemplates .
```

Bereiche in der Liste ankreuzen (Leertaste), mit Enter bestätigen, bei Nachfrage die Bibliothek wählen - fertig.
Danach:

```bash
code .                      # VS Code öffnen, empfohlene Erweiterungen installieren
uv run robotcode robot      # Beispieltests ausführen, dann results/report.html öffnen
```

Eine bestimmte Robot-Framework-Version (ein Branch je Version):

```bash
uvx copier copy --trust --vcs-ref rf-7.5.1 https://github.com/FloJoch/robotframework-copiertemplates .   # Robot Framework 7.5.1 (neueste)
uvx copier copy --trust --vcs-ref rf-7.4.2 https://github.com/FloJoch/robotframework-copiertemplates .   # Robot Framework 7.4.2
```

Ein Projekt später aktualisieren und auf seiner Version bleiben:

```bash
uvx copier update --trust --vcs-ref rf-7.5.1    # oder rf-7.4.2
```

## Dokumentation

| Thema | Inhalt |
|-------|--------|
| [Erste Schritte](docs/getting-started.de.md) | Projekt anlegen im Detail, der Dialog, ohne Dialog, häufige Probleme |
| [Erzeugte Projekte](docs/generated-projects.de.md) | Aufbau (keyword-getrieben, Screenplay), Keyword-Kennzeichnung, Agent Skills, weitere Bibliotheken |
| [Versionen und Updates](docs/versions-and-updates.de.md) | Robot-Framework-Versionen, `copier update`, eigene Kopie als Quelle |

Jedes erzeugte Projekt hat außerdem eine eigene README mit allen Details zu den gewählten Bibliotheken.
