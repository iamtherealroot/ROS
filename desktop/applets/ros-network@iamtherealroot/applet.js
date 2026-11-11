/* ROS Network v1.0: independent, read-only NetworkManager state indicator.
 * Deliberately leaves network@cinnamon.org installed during first tests.
 */
const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const NM = imports.gi.NM;
const GLib = imports.gi.GLib;
const Util = imports.misc.util;


class ROSNetwork extends Applet.IconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this._path = metadata.path;
        this._client = null;
        this._signalIds = [];
        this._timeoutId = 0;
        this.set_applet_icon_path(this._path + '/disconnected.svg');
        this.set_applet_tooltip('ROS Network: Verbindungsstatus wird ermittelt …');
        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);
        this._status = new PopupMenu.PopupMenuItem('Netzwerkstatus wird ermittelt …', {reactive: false});
        this.menu.addMenuItem(this._status);
        this._details = new PopupMenu.PopupMenuSection();
        this.menu.addMenuItem(this._details);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        let connections = new PopupMenu.PopupMenuItem('Verbindungen bearbeiten …');
        connections.connect('activate', () => Util.spawnCommandLine('nm-connection-editor'));
        this.menu.addMenuItem(connections);
        let settings = new PopupMenu.PopupMenuItem('Netzwerkeinstellungen öffnen');
        settings.connect('activate', () => Util.spawnCommandLine('cinnamon-settings network'));
        this.menu.addMenuItem(settings);
        try {
            this._client = NM.Client.new(null);
            for (let name of ['notify::state', 'notify::nm-running', 'active-connection-added', 'active-connection-removed']) {
                try {
                    this._signalIds.push(this._client.connect(name, () => this._update()));
                } catch (e) {
                    global.logError(e);
                }
            }
            this._update();
            // Backstop for missed NetworkManager signals.
            this._timeoutId = GLib.timeout_add_seconds(GLib.PRIORITY_DEFAULT, 15, () => {
                this._update();
                return GLib.SOURCE_CONTINUE;
            });
        } catch (e) {
            global.logError(e);
            this._setStatus(false, 'NetworkManager ist nicht verfügbar');
        }
    }

    _setStatus(connected, message) {
        this.set_applet_icon_path(this._path + (connected ? '/connected.svg' : '/disconnected.svg'));
        this.set_applet_tooltip('ROS Network: ' + message);
        this._status.label.text = message;
        this._refreshDetails();
    }

    _refreshDetails() {
        if (!this._details)
            return;
        this._details.removeAll();
        if (!this._client)
            return;
        let items = [];
        try {
            for (const active of this._client.get_active_connections()) {
                const name = active.get_id() || 'Unbenannte Verbindung';
                const type = active.get_connection_type() || '';
                if (type === 'vpn')
                    items.push('VPN: ' + name);
                else
                    items.push('Aktiv: ' + name);
            }
        } catch (e) {
            global.logError(e);
        }
        if (items.length === 0)
            items.push('Keine aktiven Verbindungen');
        for (const line of items.slice(0, 12))
            this._details.addMenuItem(new PopupMenu.PopupMenuItem(line, {reactive: false}));
    }

    _update() {
        if (!this._client)
            return;
        try {
            const state = this._client.get_state();
            // "Verbunden" means a NetworkManager-managed network link is active;
            // this does not promise actual Internet access.
            const connected = state >= NM.State.CONNECTED_LOCAL;
            this._setStatus(connected, connected
                ? 'Verbundene Wurzel – Netzwerkverbindung aktiv'
                : 'Getrennte Wurzel – keine aktive Netzwerkverbindung');
        } catch (e) {
            global.logError(e);
            this._setStatus(false, 'Netzwerkstatus nicht verfügbar');
        }
    }

    on_applet_clicked() {
        this._update();
        this.menu.toggle();
    }

    on_applet_removed_from_panel() {
        if (this._timeoutId)
            GLib.Source.remove(this._timeoutId);
        if (this._client) {
            for (const id of this._signalIds) {
                try { this._client.disconnect(id); } catch (e) { global.logError(e); }
            }
        }
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new ROSNetwork(metadata, orientation, panelHeight, instanceId);
}
