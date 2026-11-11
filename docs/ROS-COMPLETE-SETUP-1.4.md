# ROS Complete Setup 1.4 – Ein-Befehl-Installation (Preview)

Ziel: Den Aufwand der bisher getrennten ROS-Desktop- und LightDM-Schritte
für neue Linux-Mint-Systeme drastisch reduzieren.

Voraussetzung: Linux Mint 22.3 mit Cinnamon 6.6.9, ein lokaler
angemeldeter Desktop-Benutzer und ein geklontes ROS-Repository
(`~/ROS-Source`, Branch `develop`).

## Installation

Vorher **Hyper-V-Prüfpunkt erstellen und offene Arbeit sichern**.
Als normaler Desktop-Benutzer, **ohne sudo**:

```bash
cd ~/ROS-Source
git pull --ff-only
bash scripts/install-ros-complete.sh --reboot
```

Diese Routine aktualisiert die apt-Paketlisten, installiert bei Bedarf
`terminator` und `lightdm-gtk-greeter` mit sudo, führt bei Bedarf die
gesicherte Desktop-Stage aus, aktiviert ROS Menu / Network Native /
Power Tree und installiert die ROS-LightDM-Dateien mit Backup.
Anschließend führt sie den read-only Desktop-Audit aus und startet den
Rechner nach erfolgreich durchgeführten Shell-Befehlen neu.

**Ohne automatischen Neustart:** `bash scripts/install-ros-complete.sh`.
Bestehende ROS-Applet-Dateien werden bei erkannter Installation nicht
hot-swapped. Unterschiedliche Versionen sind ggf. separat gemäß
`prepare-ros-menu-1.1.py` zu aktualisieren.

## Warum nach dem Login noch der alte Bildschirm angezeigt werden kann

`sudo lightdm --show-config` kann schon
`greeter-session=lightdm-gtk-greeter` ausweisen, während eine laufende
LightDM-Greeter-Instanz noch nicht neu geladen wurde. Ein vollständiger
Neustart ist für den Test verlässlicher als nur eine Abmeldung.

Der bestehende `slick-greeter` muss **nicht deinstalliert** werden.
Die in `90-ros.conf` festgelegte Greeter-Sitzung ist ausschlaggebend.

Wenn auch nach einem Neustart noch das Mint-Design erscheint:
```bash
sudo lightdm --show-config | grep greeter-session
cat /etc/lightdm/lightdm-gtk-greeter.conf
journalctl -b -u lightdm --no-pager | tail -60
```

## Grenzen der Vorschau

- Erfordert ein bereits vorhandenes Repository und Git. Der
  Installer selbst lädt keinen fremden Code nach.
- Die Installation wird mit Dateibackups und Panel-Backups versehen,
  aber ist **keine atomare Ein-Schritt-Transaktion**.
- Der Audit unterscheidet technische Einrichtung von visuellen und
  funktionalen Klicktests; die müssen weiterhin manuell erfolgen.
- Auf einem angepassten bestehenden Desktop bleiben installierte
  Applet-Dateien unverändert. Theme-/Icon-Einstellungen werden nur
  durch die bestehende Desktop-Stage verwaltet.
- Der Boot-ISO-Installer ist noch nicht fertig. Diese Vorschau dient
  der Installation auf einer bereits gestarteten Mint-Sitzung.
