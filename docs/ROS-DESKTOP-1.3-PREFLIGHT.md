# ROS Desktop 1.3 – Vorbereitung Development → Test

Stand: GitHub-Branch `develop`. Die drei Desktop-Applets sind
`ros-menu@iamtherealroot`, `ros-network-native@iamtherealroot`
und `ros-power-tree@iamtherealroot`.

**Die bisherige Desktop-Installation 1.2 wird durch diese Vorbereitung
noch nicht verändert.** Es gibt kein neues ISO-Image und keine automatische
Migration, solange die kritischen Funktionstests nicht abgeschlossen sind.

## 1. Audit auf ROS-Development

```bash
cd ~/ROS-Source
git pull --ff-only
python3 -m py_compile scripts/audit-ros-desktop.py
python3 scripts/audit-ros-desktop.py
```

Dieses Skript prüft read-only: Cinnamon Panel-IDs, Vorhandensein der
Applet-Dateien, JS-Abgleich zum Repository für Menu und Power Tree,
Duplikate, Cinnamon-Theme, Icon-Theme und LightDM-Konfiguration.

Es verändert weder Panel noch Netzwerkkonfiguration noch Themes.
**WARN** auf ROS-Test ist zunächst normal, weil dort noch keine
ROS Network Native Freigabe installiert wurde.

## 2. Entscheidende manuelle Tests auf ROS-Development

- ROS Menu: Kategorie `Internet` mehrfach anklicken. Kein Programm
  darf dadurch gestartet werden. Ein Klick auf eine Anwendungskachel
  muss genau die ausgewählte Anwendung öffnen.
- Suche, Büro/System/Zubehör und Favoriten ausprobieren.
- Programm-Kacheln: zwei Spalten, korrekte Breite, kein unerwünschter
  Balken, Mausradscrollen; keine Rahmen.
- Sperren, Abmelden und Systemdialoge sichtbar, farblich unterscheidbar.
- ROS Network Native: Netzwerkmenü vollständig, Wurzel wechselt
  grün/grau je nach Verbindungsstatus.
- Power Tree korrekt und Panel-Layout ohne doppelte Netzwerk-Icons.

## 3. Erst danach ROS-Test

Die ROS-Test-VM erhält nach erfolgreicher Freigabe denselben Stand aus
GitHub, jedoch **keine Kopie** der Benutzerkonfiguration der Development-
VM: ROS-Dark auf Test, ROS-IT auf Development, eigene Logins und Passwörter.

Vor der Migration einen Hyper-V-Prüfpunkt erstellen. Anschließend erst
den neuesten Git-Stand ziehen, read-only Audit ausführen und den
kontrollierten Rollout Schritt für Schritt beginnen. Die neue Version
wird nicht automatisch durch `git pull` aktiv.

## 4. Desktop Installer 1.3 und ROS-ISO

Nach bestätigtem ROS-Test wird `scripts/install-desktop.py` um geprüfte
Desktop-Routen und einen sicheren, rücksetzbaren Panel-Aktivierungsweg
erweitert. Ein Live-/Install-ISO folgt erst nach eigenständigem
Boot-, Login-, Installer- und Benutzerprofiltest.
