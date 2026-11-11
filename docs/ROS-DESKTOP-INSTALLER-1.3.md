# ROS Desktop Installer 1.3.1 — gestufte Einrichtung

Branch: `develop`. Unterstützt **Linux Mint 22.3, Cinnamon 6.6.9**.
Für den angemeldeten Benutzer, **ohne `sudo`**.

## Warum gestuft?

Ein aktives Cinnamon-Applet zu überschreiben kann durch den
JavaScript-Modulcache zu Ausfällen führen. Darum trennt ROS 1.3:

1. **Plan** (Standard, read-only): `python3 scripts/install-ros-desktop-1.3.py`
2. **Stage** (Dateien installieren, Panel unangetastet):
   `python3 scripts/install-ros-desktop-1.3.py --stage`
3. **Activate** (einmalige, gesicherte Panel-Konfiguration):
   `python3 scripts/install-ros-desktop-1.3.py --activate`

Ein aktives ROS Menu, dessen Datei vom Git-Stand abweicht, **wird nicht
heiß überschrieben**. Die Stage-Phase bricht dann vor dem Installieren ab.
Für ältere Menüversionen den bisherigen sicheren Workflow mit
`scripts/prepare-ros-menu-1.1.py` und grafischer Neuanmeldung nutzen.

## Inhalt

- Bestehenden Desktop Installer 1.2 für die ROS-Themes, Icons, Power Tree,
  Designeinstellungen und Terminalstarter mit dessen **eigener
  Datensicherung** wiederverwenden. Eine bereits ausgewählte ROS-Theme-
  Variante bleibt erhalten. Installer 1.2 plant bei neuen Benutzern
  ROS-Dark und setzt den First-Login-Helfer.
- ROS Menu aus dem Repository sicher installieren, falls noch nicht
  vorhanden; eine inaktive ältere Kopie wird vor Ersetzung gesichert.
- ROS Network Native nur erstellen, wenn es bislang nicht vorhanden ist;
  die Quelle ist Cinnamon 6.6.9. Bestehende native Netzwerkdateien bleiben
  erhalten.
- Vor Aktivierung Panel-IDs prüfen und **nur** Menü- und Netzwerk-Applet
  umstellen. Power Tree wird, wenn noch nicht vorhanden, anstelle des Standard-\n  Power-Applets aktiviert. Fehlt das Standard-Applet, wird Power Tree\n  rechts neben dem Soundsymbol ergänzt, ohne andere Applet-IDs zu ändern. Doppelte bisherige Netzwerkanzeigen können entfernt werden.
- Komplettes Panel vor Änderungen sichern und nach Möglichkeit
  über `--restore-panel` zurücksetzen. Wiederherstellung verweigert
  das Überschreiben zwischenzeitlicher Panel-Änderungen.

**Keine Änderungen an** LightDM, Systembenutzern,
Netzwerkschnittstellen/IP-Adressen, Firewall, Passwörtern oder der
ausgewählten ROS-Theme-Variante.

## ROS-Development und ROS-Test

Beide bestehenden VMs wurden mit dem Audit erfolgreich geprüft.
Daher zuerst nur die neue Planung ausführen:

```bash
cd ~/ROS-Source
git pull --ff-only
python3 -m py_compile scripts/install-ros-desktop-1.3.py
python3 scripts/install-ros-desktop-1.3.py
```

Auf bereits vollständig eingerichteten VMs ist **kein** weiteres
`--stage` oder `--activate` erforderlich. Der Installer ist zunächst
für saubere Testkonten/neue Systeme vorgesehen.

## Neues Testkonto / neue VM

Nach Hyper-V-Prüfpunkt:

```bash
cd ~/ROS-Source
python3 scripts/install-ros-desktop-1.3.py
python3 scripts/install-ros-desktop-1.3.py --stage
python3 scripts/install-ros-desktop-1.3.py --activate
```

Danach grafisch ab- und wieder anmelden und prüfen:

```bash
python3 scripts/audit-ros-desktop.py
```

Ist ROS Power Tree noch nicht aktiv, ergänzt \`--activate\` das Applet\n  vorsichtig und legt zuvor ein Panel-Backup an. Ist kein eindeutiger\n  Einfügepunkt vorhanden, bricht es ohne Panel-Änderung ab.\n\n  **Nachtrag 1.3.1:** Bei bereits installiertem Menü und Netzwerk, aber\n  fehlendem Power Tree, genügt \`python3 scripts/install-ros-desktop-1.3.py --activate\`.\n  \`--stage\` muss nicht erneut ausgeführt werden.\n\n  Die LightDM-WARN-Wertung auf frischen Installationen bleibt vorerst\n  korrekt: Die systemweite ROS-Login-Konfiguration gehört noch nicht\n  zur per-user Installation.

## Rücksetzen

Der `--activate`-Schritt gibt den Sicherungspfad aus, z. B.

```bash
python3 scripts/install-ros-desktop-1.3.py --restore-panel ~/.config/ros/backups/desktop-1.3-panel-<ZEITSTEMPEL>
```

Dies stellt **nur das Panel** wieder her. Für Desktop-Dateien und
GSettings gibt die `--stage`-Phase einen eigenen Backup-Pfad des
Desktop Installers 1.2 aus:
`python3 scripts/install-desktop.py --restore <BACKUP-PFAD>`.
Für aktualisierte Menüdateien wird gegebenenfalls ein zusätzliches
`desktop-1.3-menu-...`-Dateibackup geschrieben.
Diese Sicherungen sind bewusst getrennt: Es gibt **keinen
transaktionsweiten automatischen Rollback**.

## Status

Der Installer ist im GitHub-Branch `develop` committed, aber noch nicht
auf einer frischen Cinnamon-VM durchgetestet. Vor einer ISO-Freigabe:
Neuinstallation, Aktivierung, Rollback, erste Anmeldung,
Kategorie-Klicks, Netzwerksymbol und Theme-Erhalt real prüfen.
