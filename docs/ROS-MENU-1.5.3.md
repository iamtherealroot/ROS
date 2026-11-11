# ROS Menu 1.5.3 Preview — Kategorie-Klickfehler

Auf ROS-Development wurde gemeldet, dass ein Klick auf die Kategorie
**Internet** unbeabsichtigt den Taschenrechner startet. Das darf nicht
passieren. Der Code trennt Kategorie-Auswahl und Anwendungsstart:

- Kategorie-Klicks setzen nur den Filter; sie starten kein Programm.
- Während der UI-Aktualisierung wird ein sofortiger unbeabsichtigter
  Folge-Klick auf eine Anwendung für 450 ms ignoriert.
- Desktop-Kategorien stammen nach Möglichkeit aus
  `Gio.DesktopAppInfo` und werden auf freedesktop-Kategorien gemappt.
  `Utility/Calculator` gehört nicht zur Internet-Kategorie.
- GLib-Monotonic-Time verwendet eine tatsächliche Uhr für den Klickschutz.

Die Ursache des unbeabsichtigten Anwendungsstarts ist durch die
vorliegenden Informationen noch nicht abschließend bewiesen. Diese
Änderungen sind gezielte Schutzmaßnahmen und müssen in Cinnamon 6.6.9
grafisch geprüft werden.

## Upgrade auf ROS-Development

Hyper-V-Prüfpunkt erstellen. Als `ichbinroot`, nicht mit sudo:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/prepare-ros-menu-1.1.py
```

Der historische Updater installiert den aktuellen Code, also 1.5.3.
Dann grafisch abmelden und erneut anmelden, anschließend:

```bash
cd ~/ROS-Source
python3 scripts/install-ros-menu.py --activate
```

Prüfen: Internet anklicken → ausschließlich Internetprogramme anzeigen;
Taschenrechner darf NICHT automatisch öffnen. Danach bewusst einen
Internet-Eintrag anklicken und verifizieren, dass genau dieser startet.
Weitere Kategorien, Suche und Favoriten ebenfalls testen.

Falls das Menü wieder ausfällt, über den ausgegebenen Aktivierungs-Backup
`python3 scripts/install-ros-menu.py --restore <PFAD>`
das Cinnamon-Startmenü zurückholen.

**Keine Übernahme auf ROS-Test oder die ISO vor bestandenem Funktionstest.**
