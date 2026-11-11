# ROS ISO 0.1 — erster ISO-Build und Installationsprofil-Vorschau

**Status: Build-Prototyp, keine installationsfertige ROS-Distribution.**

Basis: originale Linux Mint 22.3 Cinnamon x86_64 ISO. Die offiziellen
Mint-Installationsprogramme werden derzeit **nicht** durch den
ROS-Installer ersetzt. Wer den normalen Mint-Installer ausführt,
installiert weiterhin Mint. Die ROS-Profilauswahl ist vorläufig ein
eigenes GTK-Fenster, das ausschließlich eine JSON-Auswahl speichert.

## Beschlossene ROS-Installation

Zwei Installationswege: **Vereinfachte Installation** und
**Experteninstallation**. Vier Profile: **Minimale Installation**,
**IT**, **Gaming**, **Gesamte Installation**.
Diese Profile sind keine Design-Themes. Alle Profile sollen später
vollständig offline von derselben ISO installiert werden können.

Die maschinenlesbare Definition liegt in `iso/profiles.json`.

## 1. Voraussetzungen auf einer Linux-Mint-Build-VM

Ausreichend Speicher für Original-ISO, Ausgabe-ISO und temporäre
Projektdateien bereithalten (mindestens ca. 15 GB frei).
Die Original-ISO benötigt man nur einmal. Als normaler Benutzer:

```bash
sudo apt update
sudo apt install -y xorriso git python3
cd ~/ROS-Source
git pull --ff-only
```

Eine *unveränderte* Linux Mint 22.3 Cinnamon x86_64 ISO herunterladen,
z. B. von
`https://pub.linuxmint.io/stable/22.3/linuxmint-22.3-cinnamon-64bit.iso`.
Checksumme gegen die **offizielle signierte Hashdatei** verifizieren.
Niemals eine ISO mit unbekannter Herkunft als Basis verwenden.

## 2. Build-Vorschau

Beispiel: Basis-ISO wurde in `~/Downloads` gespeichert.

```bash
cd ~/ROS-Source
bash scripts/build-ros-iso.sh \
  --base "$HOME/Downloads/linuxmint-22.3-cinnamon-64bit.iso" \
  --output "$HOME/Downloads/ROS-0.1-preview.iso" \
  --dry-run
```

Das liest die Bootinformationen und prüft das Profilmanifest,
ohne ein ISO zu erzeugen.

## 3. Erste ROS-Live-ISO erstellen

```bash
cd ~/ROS-Source
bash scripts/build-ros-iso.sh \
  --base "$HOME/Downloads/linuxmint-22.3-cinnamon-64bit.iso" \
  --output "$HOME/Downloads/ROS-0.1-preview.iso"
```

Der Builder legt `/ros/source` mit den *committeten* ROS-Dateien
auf der ISO ab, kopiert das Profilmanifest nach `/ros` und versucht,
die Boot-Einträge der Original-ISO mit `xorriso -boot_image any replay`
zu erhalten. Danach schreibt er `.sha256`.

**Der Builder verändert nicht das Mint-SquashFS.** Das ROS-Desktop-
Erlebnis im Live-System ist deshalb noch nicht automatisch aktiv.
Eine Ausgabe-ISO gilt nicht als bootfähig, bevor sie in VMs getestet ist.

## 4. Test in einer frischen Hyper-V-/QEMU-VM

- UEFI starten, prüfen, ob das Mint-Live-System bootet.
- Prüfen, ob `/cdrom/ros/source/iso/profiles.json` vorhanden ist.
- GTK-Auswahlfenster öffnen (im Live-System):

```bash
python3 /cdrom/ros/source/iso/installer/select-profile.py
```

- Jeweils die vier Profile und beide Installationswege auswählen;
  die JSON-Ausgabe `~/ros-install-plan.json` kontrollieren.
- Testen, dass die Auswahl **keine Partitionierung und keine
  Installation** startet.
- Weitere VM mit Legacy-BIOS starten, um die zweite Bootvariante
  zu verifizieren.
- Datenträger **nicht** als ROS-Test installieren, solange noch
  der originale Mint-Installer gestartet wird.

## 5. Arbeit bis zur installationsfertigen ISO

1. Offline-Paketarchiv für alle vier Profile inkl. abhängiger
   Bibliotheken, 32-Bit-Gaming-Paketen und Drittanbieter-Lizenzen.
2. ROS-SquashFS/Live-Desktop in der ISO erzeugen und ROS-Login,
   ROS Menu, Power Tree und Network Native einbauen.
3. Grafischen Installer über Ubiquity/Calamares oder geprüften
   Installations-Backend-Integrationsweg implementieren: Sprache,
   Tastatur, LUKS, Festplattenwahl, Expertenpartitionierung,
   Benutzerkonto, vier Profile und explizite Löschfreigabe.
4. Offline-Vollinstallation in frischen UEFI-/BIOS-VMs testen.
5. Prüfen, dass alle Profile nach erstem Boot ohne Internetzugang
   korrekt funktionieren und das gewählte Profil erhalten bleibt.
6. Boot- und Installationsfehler abfangen sowie Wiederherstellung
   und Fehlerprotokolle bereitstellen.

Erst nach bestandenen Tests darf ROS als **installationsfertig**
bezeichnet werden.
