# ROS ISO — verbindliche Installationsmodi und Profile

Diese Spezifikation übernimmt die bereits am 10. November 2026 festgelegten Entscheidungen für **Root Operating System (ROS)**. Sie ist die Grundlage für die bootfähige, vollständig offline installierbare ROS-ISO.

## Zwei Installationswege

### Vereinfachte Installation
Geführter Ablauf mit empfohlenen Voreinstellungen:
1. Sprache wählen
2. Tastaturlayout wählen
3. Installationsziel auswählen
4. Benutzername eingeben
5. LUKS-Passwort festlegen
6. Eines der vier Systemprofile wählen
7. Änderungen und Datenträger-Löschung zusammenfassen und ausdrücklich bestätigen
8. Offline installieren und neu starten

### Experteninstallation
Bietet zusätzlich individuell einstellbare:
- Partitionierung und Dateisystem
- Verschlüsselung inklusive LUKS
- Bootloader
- Netzwerkkonfiguration
- Benutzerkonten
- Einzelne Programme/Module

Vor Änderungen an Partitionen und Datenträgern ist eine vollständige Zusammenfassung mit ausdrücklicher Bestätigung zwingend.

## Vier Systemprofile

### 1. Minimale Installation (Minimal System)
ROS Cinnamon Desktop, Firefox, LibreOffice, Bitwarden, Timeshift, ROS Welcome, ROS Have-To und grundlegende Systemwerkzeuge.

### 2. IT (IT System)
Alles aus der minimalen Installation **plus** WireGuard, Wireshark, SSH, Git/GitHub CLI, KVM/QEMU und virt-manager.

### 3. Gaming (Gaming System)
Alles aus der minimalen Installation **plus** Steam, Heroic, GameMode, Vulkan- und 32-Bit-Bibliotheken sowie Ubisoft Connect über Wine/Proton beziehungsweise den ROS Ubisoft Installer.

### 4. Gesamte Installation (Komplettinstallation)
Alle Module des IT- und Gaming-Systems zusammen mit den Basisprogrammen.

## Verbindliche Architekturregeln

- **Eine einzige ISO** enthält die vollständige Offline-Paketbasis für alle vier Profile. Keine während der Installation erforderlichen Downloads.
- Die Profilwahl ist **keine Theme-Auswahl**: ROS Dark, Gaming, IT, Creator, Stealth und Nordic sind unabhängig davon später auswählbare Desktop-Designs.
- Benötigte Treiber werden abhängig von der erkannten Hardware ausgewählt.
- Nicht gewählte Module können später über **ROS Have-To** ergänzt werden.
- Beide Installationswege unterstützen LUKS.
- ROS Desktop, ROS Menu, ROS Network Native, ROS Power Tree und ROS Login werden als gemeinsames Grundsystem eingebunden.
- Es wird keine Installation und keine Datenträgeränderung ohne explizite Benutzerfreigabe durchgeführt.

## Nächste Implementierungsschritte

1. Reproduzierbare lokale Offline-Paketablage und Paketmanifest je Profil.
2. Grafische ROS-Installer-Oberfläche mit den zwei Installationswegen, vier Profilen und verbindlicher Bestätigungsseite.
3. Zuverlässige Systeminstallation einschließlich Benutzerprofil, LUKS, EFI/Bootloader und ROS-LightDM.
4. Remastering eines Linux Mint 22.3 Cinnamon x86_64 Live-/Installationsabbilds zu einer bootfähigen ROS-ISO.
5. Testmatrix für alle vier Profile und beide Installationswege in frischen VMs (UEFI, Datenverschlüsselung, Offlinefähigkeit, Reboot, Login und Rollback).

**Status:** Verbindliche Produktspezifikation; noch keine fertig gebaute oder getestete ISO.
