# ROS Menu 1.3 Preview — ROS-Development

Optimierungen gegenüber ROS Menu 1.2 anhand des Hyper-V-Screenshots:
- Anwendungsliste: fest ausgerichtete volle Zeilen, Icons und Namen linksbündig
- Kategorien: einheitliche Breite auch beim aktiven Eintrag
- Favoriten: wenn verfügbar echte Desktop-Anwendungsicons
- Etwas geringere Menü- und Listenhöhe, weniger ungenutzter Raum
- Direkte Systemaktionen bleiben sichtbar

**Status:** Auf GitHub `develop` implementiert; grafischer Test auf
ROS-Development ist noch ausstehend. Nicht auf ROS-Test oder in die ISO
übernehmen, bevor die Funktionen geprüft wurden.

## Upgrade auf ROS-Development

In Hyper-V vorab einen Prüfpunk erstellen. Als `ichbinroot`, ohne sudo:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/prepare-ros-menu-1.1.py
```

Dieser bereits vorhandene Upgrade-Helfer verwendet immer den *aktuellen*
Quellcode; trotz Dateiname `1.1` wird ROS Menu 1.3 installiert. Die
alte Applet-Version wird gesichert und das originale Cinnamon-Menü
vorübergehend aktiviert. Jetzt **grafisch abmelden und erneut anmelden**.

```bash
cd ~/ROS-Source
python3 scripts/install-ros-menu.py --activate
```

Aktivierungs-Backup-Pfad notieren. Bei Problemen mit demselben Skript
`--restore <BACKUP-PFAD>` das originale Cinnamon-Menü wiederherstellen.

Test: Programmnamen und Icons linksbündig, Kategorien gleich breit,
Favoriten starten die Programme, Suche findet Programme, Systemknöpfe
funktionieren wie gewohnt. Falls Cinnamon alten JavaScript-Code nutzt,
erneut grafisch abmelden/anmelden.

Die Version 1.3 passt nur das ROS-Menü an. ROS Network Native und
Power Tree werden nicht verändert.
