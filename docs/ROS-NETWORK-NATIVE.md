# ROS Network Native – Preview für ROS-Development (Cinnamon 6.6.9)

Anstatt das Cinnamon-Netzwerkmenü in einem neuen Applet unvollständig
nachzubauen, erzeugt `scripts/install-ros-network-native.py` **lokal**
eine angepasste Kopie der auf dem Rechner installierten
`network@cinnamon.org`-Implementierung. Die einzige gezielte Änderung im
JavaScript ist der Aufruf zur **Panel-Icon-Darstellung** in `_setIcon`.
Menü, WLAN-Verbindungsauswahl, VPN, Netzwerkstatus und Einstellungen
bleiben dadurch aus der Originalimplementierung erhalten.

Zwei SVGs kennzeichnen **verbunden** und **getrennt**. Offline,
keine Route und Verbindungsaufbau zeigen derzeit die getrennte Wurzel.
Das Symbol bildet Cinnamon-/NetworkManager-Zustände ab und beweist keinen
Internetzugang. Da ROS Icons auf zwei Zustände reduziert, fallen einzelne
Original-Piktogramme, etwa VPN-Indikatoren, im Panelsymbol weg; ihr
Verbindungsstatus bleibt im Netzwerkmenü.

## Nur auf ROS-Development testen

1. Hyper-V-Prüfpunkt erstellen.
2. Als grafisch angemeldeter Benutzer `ichbinroot` (nie sudo):

```bash
cd ~/ROS-Source
git pull --ff-only
python3 -m py_compile scripts/install-ros-network-native.py
python3 scripts/install-ros-network-native.py --install
python3 scripts/install-ros-network-native.py --activate
```

Die native Netzwerkanzeige wird **nicht entfernt**. ROS Network Status
und ROS Network Native dürfen vorübergehend zusätzlich sichtbar sein.
Der Aktivierungsbefehl zeigt den Backup-Pfad, z.B.:

```bash
python3 scripts/install-ros-network-native.py --restore ~/.config/ros/backups/ros-network-native-TIMESTAMP
```

Testen: Öffnet die Wurzel exakt das originale Cinnamon-Netzwerkmenü?
Funktioniert die WLAN-Liste, werden VPN und Netzwerkeinstellungen
angezeigt? Beobachte die Wurzelzustände. Trenne keine Netzverbindungen
während einer SSH-Sitzung.

Bei Absturz: `grep -i -A 20 'ros-network-native@iamtherealroot' ~/.xsession-errors | tail -80`.
**Noch nicht auf ROS-Test ausrollen oder in die ISO einbauen.**
Wenn der lokale Ableger die Tests besteht, folgt die Vereinheitlichung
der Netzwerk-Applets und ein Updateverfahren für Cinnamon-Versionswechsel.

Der angepasste Cinnamon-Code wird absichtlich auf dem Zielsystem aus
der bereits installierten Originalversion erzeugt und nicht als Kopie
einer Mint-Systemdatei ins ROS-Repository committed.
