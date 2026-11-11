# Erzeugte Projekte

[English](generated-projects.md) | **Deutsch**

[← zurück zur README](../README.de.md)

## Aufbau der erzeugten Projekte

Die Tests sind **keyword-getrieben** und folgen dem **Screenplay-Muster** (ohne Actor). Ein Testfall ist eine
Folge fachlicher Keywords mit Argumenten - jede Zeile ist eine Handlung (Task) oder eine Prüfung (Assertion):

```robotframework
Product Lands In The Cart
    Open Login Page
    Log In
    Add Product To Cart    sauce-labs-backpack
    Element Should Show Text    ${MAIN_CART_BADGE}    1
```

Der Test liest sich wie die Spezifikation und ist genau das, was ausgeführt wird. Keywords werden in vielen
Tests wiederverwendet, Testdaten stehen sichtbar als Argumente, Handeln und Prüfen bleiben getrennt. Alles
außer den Tests liegt in `resources/`; alle Einbindungen beginnen mit `${EXECDIR}` (Projektordner).

| Schicht | Inhalt | In Tests genutzt |
|---------|--------|------------------|
| `resources/main.resource` | Standard-Bibliotheken, CryptoLibrary, Adressen und Zugangsdaten je Umgebung (dev, test, prod), globale Werte wie `${CI}`, `${BROWSER}`, `${BROWSER_SPEED}`, `${TIMEOUT}` | - |
| `resources/abilities/` | eine Datei je Bibliothek: `Library`-Import und Einstellungen (z. B. Mailserver, Datenbankverbindung), **keine Keywords** | - |
| `resources/pages/` | Page Objects, eine Datei je Seite: `login_page`, `main_page`, `cart_page`, `settings_page` - Selektoren über `id` oder `data-test` | nur Selektoren |
| `resources/interactions/` | technische Hilfs-Keywords - einzige Stelle mit Keywords der Bibliotheken; Tag `interaction` | nein |
| `resources/tasks/` | fachliche Handlungen mit Argumenten, z. B. `Add Product To Cart    sauce-labs-backpack`; auch Setup und Teardown wie `Start Browser` | ja |
| `resources/assertions/` | **allgemeine** Prüfungen, z. B. `Element Should Show Text    ${MAIN_TITLE}    Products` | ja |
| `tests/<bereich>/` | Testfälle aus Tasks und Assertions | - |

Web-Tests mit der Browser Library und die Barrierefreiheitsprüfung teilen sich eine Browser-Schicht
(`browser_ability`, `browser_interactions`) - die Browser Library wird nur einmal eingebunden.

### Empfehlung: Keywords kennzeichnen, die nicht in Tests gehören

Tests sollen auch für Fachleute mit wenig technischem Hintergrund lesbar sein. Es hilft, Keywords, die **nicht**
in einen Test gehören, auf einen Blick erkennbar zu machen, damit sie dort niemand aus Versehen nutzt. Übliche
Wege sind:

- ein **Tag** an den technischen Keywords, z. B. `Keyword Tags    interaction` in den Settings einer Datei -
  sichtbar in RobotCode, im Log und in der Keyword-Dokumentation,
- ein **Präfix** wie ein führender Unterstrich (`_Click When Ready`),
- eine **andere Sprache** für technische als für fachliche Keywords.

Die erzeugten Projekte nutzen den Tag: Jede Datei in `resources/interactions/` hat `Keyword Tags    interaction`,
und ein Test dieser Vorlage prüft, dass Tests diese Keywords nie aufrufen. Hinweis: Der eingebaute Tag
`robot:private` passt nicht für eine ganze Schicht - Robot Framework warnt bei jeder Nutzung eines privaten
Keywords aus einer anderen Datei, und Tasks rufen Interactions immer aus einer anderen Datei auf. Wähle die
Konvention, die zu deinem Team passt - entscheidend ist, dass ein Test nur lesbare fachliche Schritte enthält.

### Einfachere Struktur für kleine Projekte

Die Screenplay-Schichten lohnen sich, wenn viele Leute über längere Zeit Tests schreiben. Für ein kleines Projekt
oder einen ersten Versuch können sie zu viel sein. Dann einfach zu einer Grundstruktur zusammenlegen:

```text
tests/<bereich>/                       Testfälle
resources/keywords/<bereich>.resource  eigene Keywords: Library-Import, Handlungen und Prüfungen in einer Datei
resources/pages/                       Selektoren je Seite (behalten - sie machen Tests robust)
resources/main.resource                Standard-Bibliotheken, Umgebungen, Zugangsdaten
```

So kommst du von einem erzeugten Projekt dorthin:

1. Je Bereich `resources/keywords/<bereich>.resource` anlegen mit `Resource    ${EXECDIR}/resources/main.resource`,
   der `Library`-Zeile aus der Ability und den nötigen `Resource`-Zeilen für Pages.
2. Die Keywords aus `tasks/`, `assertions/` und `interactions/` dieses Bereichs dorthin verschieben (oder nur die
   nötigen behalten und Bibliotheks-Keywords direkt aufrufen).
3. Die Tests `resources/keywords/<bereich>.resource` statt Tasks und Assertions importieren lassen, dann die
   Ordner `abilities/`, `interactions/`, `tasks/` und `assertions/` löschen.
4. Mit `uv run robotcode -p check robot` und `uv run robocop check` prüfen.

Die Tests bleiben keyword-getrieben - nur die Schichten dahinter werden weniger. Beachte: `copier update` meldet
für die verschobenen Dateien dann Konflikte; bei einem vereinfachten Projekt ist es meist einfacher, nicht mehr
aus der Vorlage zu aktualisieren. Die wichtigste Regel bleibt gleich: Tests enthalten lesbare fachliche Schritte,
technische Details stehen in Keywords und Pages.

Andere Strukturen funktionieren genauso - die Schichten dieser Vorlage sind ein Vorschlag, keine Pflicht.
Übliche Varianten sind zum Beispiel:

- **nach Funktion oder Fachbereich:** `resources/<funktion>/` mit Keywords und Pages dieser Funktion zusammen,
- **nur Page Objects:** je Seite eine Resource-Datei mit ihren Selektoren *und* Keywords,
- **nach Testebene:** eigene Ordner für API-, UI- und End-to-End-Tests mit gemeinsamen Keywords in
  `resources/common/`.

Egal welche Struktur: Tests enthalten lesbare fachliche Schritte, Selektoren stehen an einer Stelle, Einbindungen
beginnen mit `${EXECDIR}`, und Ausführungsoptionen bleiben in den Profilen von `robot.toml`.

## Agent Skills

Jedes Projekt enthält in `.agents/skills/` drei Skills im offenen Format [Agent Skills](https://agentskills.io/)
(je Ordner eine `SKILL.md`), zugeschnitten auf die gewählten Bibliotheken:

| Skill | Wofür |
|-------|-------|
| `robot-project` | Aufbau, installierte Bibliotheken mit Doku-Links, Befehle, Regeln |
| `robot-write-test` | fachliche Testidee → keyword-getriebener Test mit den vorhandenen Tasks und Assertions |
| `robot-explain-results` | Tests ausführen und Fehler erklären (Anwendung, Test oder Umgebung) |

**Nutzung:** Den Projektordner in einem KI-Assistenten öffnen, der Agent Skills unterstützt - viele Werkzeuge
finden `.agents/skills/` automatisch. Erwartet ein Werkzeug einen anderen Ordner, die Skill-Ordner dorthin
kopieren. Ohne Skill-Unterstützung - etwa in einem reinen Chat - den Inhalt einer oder aller `SKILL.md` als
Anweisung bzw. Systemprompt einfügen: Jeder Skill ist eigenständig (Aufbau, Regeln, vorhandene Keywords), fragt
nur bei echtem Bedarf nach dem Inhalt einer Datei und antwortet mit kopierbaren Dateiblöcken. Die Skills fragen
nur das Nötigste nach und enthalten **keine internen oder persönlichen Daten**.
Schritt für Schritt für einen Web-Chat: siehe unten; Details stehen auch in der README jedes Projekts, Abschnitt
„Coding assistants (Agent Skills)“.

### Die Skills in einem Web-Chat nutzen

Klappt mit jedem Chat-Assistenten im Browser, auch ohne Dateizugriff:

1. Im erzeugten Projekt die Datei des passenden Skills öffnen, z. B.
   `.agents/skills/robot-write-test/SKILL.md` - die Dateien sind reiner Text mit den echten Angaben des Projekts.
2. Den **ganzen** Inhalt kopieren (einschließlich des Teils zwischen `---` oben).
3. In den Chat einfügen - als **eigene Anweisungen / Systemprompt / Projektwissen**, wenn der Chat das anbietet,
   sonst als **erste Nachricht** mit einem Satz wie „Nutze diese Anweisungen für dieses Gespräch.“ Für
   allgemeine Hilfe alle drei Skills nacheinander einfügen.
4. Die Frage stellen, z. B. „Schreib einen Test: Anmeldung mit falschem Passwort zeigt eine Fehlermeldung“ oder
   eine Fehlermeldung aus `results/log.html` einfügen und fragen „Warum ist dieser Test fehlgeschlagen?“.
5. Fragt der Assistent nach einer Datei, nur diese Datei einfügen (z. B. ein Page Object). Er antwortet mit
   vollständigen Blöcken je Dateipfad - diese ins Projekt übernehmen und die genannten Befehle ausführen.

Keine Zugangsdaten, Tokens oder echten personenbezogenen Daten einfügen. Nach neuen Keywords oder Bibliotheken
die Skills erneut einfügen, damit der Chat den aktuellen Stand kennt (oder kurz dazuschreiben, was sich geändert
hat).

## Weitere Bibliotheken und Werkzeuge

Der Dialog deckt bewusst nur die häufigsten Bereiche ab. Wächst ein Projekt, sind diese bekannten Ergänzungen
ein guter nächster Schritt - jede wird mit `uv add <paket>` installiert und bei Bibliotheken mit Ability und
Interactions eingebunden, wie in der Projekt-README beschrieben („Adding more libraries“). Paketnamen sind
unterschiedlich - den genauen Namen auf PyPI nachsehen. Diese Pakete sind nicht Teil der Tests der Vorlage.

| Bedarf | Paket | Hinweis |
|--------|-------|---------|
| Tests parallel ausführen | [`robotframework-pabot`](https://pypi.org/project/robotframework-pabot/) | Verkürzt lange Testläufe; Tests müssen unabhängig sein (sind sie in dieser Vorlage schon). |
| Datengetriebene Tests aus CSV oder Excel | [`robotframework-datadriver`](https://pypi.org/project/robotframework-datadriver/) | Eine Testvorlage, viele Datenzeilen, gepflegt vom Fachbereich. |
| Excel-Dateien | [`robotframework-excelsage`](https://pypi.org/project/robotframework-excelsage/) | Exporte und Importe prüfen. |
| Server und Dateien per SSH/SFTP | [`robotframework-sshlibrary`](https://pypi.org/project/robotframework-sshlibrary/) | Befehle ausführen, Dateien übertragen, Batch-Jobs prüfen. |
| Ergebnisse über die Zeit | [`robotframework-dashboard`](https://pypi.org/project/robotframework-dashboard/) | HTML-Dashboard über viele Testläufe. |
| API-Tests aus einer OpenAPI-Spezifikation | [`robotframework-openapidriver`](https://pypi.org/project/robotframework-openapidriver/) | Erzeugt Testfälle aus der Spezifikation; für Teams, die schon OpenAPI-Dateien pflegen. |
| Fehlgeschlagene Tests wiederholen | [`robotframework-retryfailed`](https://pypi.org/project/robotframework-retryfailed/) | Mit Vorsicht nutzen: Wiederholungen können echte, sporadische Fehler verdecken. |

Formatieren ist schon dabei: `uv run robocop format` (das frühere Robotidy steckt inzwischen in Robocop).

Für alles Weitere: [MarketSquare](https://github.com/MarketSquare), die GitHub-Organisation der
Robot-Framework-Community, und die Übersicht unter <https://robotframework.org/#resources>. Vor dem Einbinden
auf PyPI prüfen, ob eine Bibliothek noch gepflegt wird und zu deiner Robot-Framework-Version passt.
