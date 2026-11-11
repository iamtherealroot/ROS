# ROS Menu 1.5.5 — Layout und unbeabsichtigte Programmstarts

**Development-Vorschau, noch nicht grafisch abgenommen.**

Beobachteter Fehler auf ROS-Development: Ein Klick auf die Kategorie
"Internet" startete unbeabsichtigt den Taschenrechner oder die Bluetooth-
Geräteverwaltung. Die genaue Ursache ist nicht abschließend nachgewiesen,
die App-Liste wurde bislang aber innerhalb desselben Kategorie-Klicks
zerstört und neu aufgebaut.

1. Kategorie-Klick räumt die alte Anwendungsliste sofort leer, ohne
   gleichzeitig neue klickbare App-Kacheln zu erzeugen.
2. Gefilterte Kacheln werden erst 350 ms später erzeugt, nachdem der
   Maus-Klick abgearbeitet werden konnte.
3. Zusätzlich blockiert der App-Start für 1,1 s nach einem Kategorie-Klick,
   um versehentliche Doppelklicks/Cross-Events zu vermeiden.
4. Suche und Kategorien lesen weiterhin Desktop-/freedesktop-Kategorien.
5. Die Anwendungsliste behält ihren Zweispaltenaufbau, wird auf 480 px
   erweitert, ist wieder bündig zu den übrigen Menüinhalten und
   entfernt alle gezeichneten Kachelrahmen/Schatten.
6. ROS-Netzwerk-Applet und Power Tree bleiben unangetastet.

## Installation nur auf ROS-Development

Hyper-V-Prüfpunkt erstellen, dann als `ichbinroot`, nicht mit sudo:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/prepare-ros-menu-1.1.py
```

Der historisch benannte Installer sichert die bisherige Menüversion.
Grafisch abmelden und wieder anmelden, danach:

```bash
cd ~/ROS-Source
python3 scripts/install-ros-menu.py --activate
```

**Funktionstest (wichtig):** Kategorie Internet anklicken, ohne dass
irgendeine Anwendung startet. Danach mindestens zwei Sekunden abwarten,
eine Internet-Anwendung auswählen und prüfen, dass nur die ausgewählte
Anwendung startet. Kategorien Büro, Spiele, Zubehör wiederholen.

**Optik:** Programmkacheln über die Listenbreite, weder Kachelrahmen noch
sichtbare Scrollbalken. Weiterhin Mausradscrollen prüfen. Bei Fehlern
aktivierungs-Backup mit
`python3 scripts/install-ros-menu.py --restore <PFAD>`
wiederherstellen und neue `~/.xsession-errors` sammeln.

ROS-Test und ISO bleiben bis zum bestandenen Test auf ihrem bisherigen Stand.
