# ROS Menu 1.5.4 – Scrollleisten und Kachelbreiten

Diese Development-Vorschau behebt den Screenshot-Fehler aus ROS Menu 1.5.3:
- Zweispaltige Programmkacheln verkleinert (200 px Inhalt plus 8 px Padding je Seite), sodass beide in die 450 px breite Liste passen
- Keine sichtbaren horizontalen oder vertikalen Scrollleisten; die Liste bleibt über Mausrad bzw. Scroll-Geste bedienbar
- Keine Rahmen um die Programmkacheln, nur dezenter, halbtransparenter Hintergrund
- Unverändert: Kategorien, Programmsuche, Favoriten, vier farbige Systemaktionen

## Nur ROS-Development

Vorher einen Hyper-V-Prüfpunkt anlegen. Als `ichbinroot` und ohne sudo:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/prepare-ros-menu-1.1.py
```

Der Upgrade-Helfer hat einen historischen Namen, verwendet aber den aktuellen ausgecheckten Code. Vollständig grafisch abmelden und wieder anmelden, dann:

```bash
cd ~/ROS-Source
python3 scripts/install-ros-menu.py --activate
```

Den ausgegebenen Sicherungspfad aufbewahren. Prüfen, ob kein
horizontaler Balken mehr zu sehen ist und ob die Programmliste weiterhin
mit dem Mausrad vertikal scrollt. Bei einem Fehler mit
`python3 scripts/install-ros-menu.py --restore <Aktivierungs-Backup>`
auf Cinnamon-Menü zurückwechseln. Noch nicht für ROS-Test/ISO freigegeben.
