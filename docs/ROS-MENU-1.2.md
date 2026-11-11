# ROS Menu 1.2 – kompakter Startmenü-Prototyp

**Status:** Code in `develop`, noch nicht grafisch auf ROS-Development
abgenommen. ROS-Test bleibt unverändert.

Nach Feedback zum ROS Menu 1.1 wurde die große zweispaltige Oberfläche
durch eine kompaktere, vertikale Anordnung ersetzt:

1. ROS-Titel und gut sichtbare Anwendungssuche
2. Sofort sichtbare Favoriten: Dateien, Firefox, ROS Terminal
3. Kategorien als dreispaltige Schaltflächen, keine lange linke Leiste
4. Eine breitere, scrollbar angelegte Anwendungsliste
5. Direkt erreichbare Sitzungsaktionen unten

## Entwicklungstest auf ROS-Development

- Vorher Hyper-V-Prüfpunkt erstellen.
- Als `ichbinroot` ohne sudo:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 scripts/prepare-ros-menu-1.1.py
```

Der Name des bestehenden Upgrade-Helfers enthält noch `1.1`, er
installiert aber stets den **aktuell ausgecheckten** ROS-Menu-Code.
Er sichert die vorige Applet-Version und schaltet vorübergehend auf das
originale Cinnamon-Menü. **Grafisch abmelden und wieder anmelden**, damit
Cinnamon das JavaScript-Modul neu einliest. Anschließend:

```bash
cd ~/ROS-Source
python3 scripts/install-ros-menu.py --activate
```

Backup-Pfad aus dem Aktivierungsbefehl notieren; bei Problemen mit
`python3 scripts/install-ros-menu.py --restore <BACKUP-PFAD>` den
ursprünglichen Cinnamon-Startbutton zurückholen.

Grafische Abnahme: Fensterhöhe, Programmnamen und Icons, Kategorie-Wechsel,
Suchergebnisse, Start von Nemo/Firefox/Terminal, Sitzungsdialoge und keine
Überlappungen. Kein Release/ISO-Rollout vor erfolgreichem Test.
