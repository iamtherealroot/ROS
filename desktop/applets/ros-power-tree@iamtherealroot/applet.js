const Applet = imports.ui.applet;
const GLib = imports.gi.GLib;
const Gio = imports.gi.Gio;
const Mainloop = imports.mainloop;
const UUID = 'ros-power-tree@iamtherealroot';

class RosPowerTree extends Applet.TextIconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this._path = imports.ui.appletManager.appletMeta[UUID].path;
        this._timer = 0;
        this._refresh();
        this._timer = Mainloop.timeout_add_seconds(15, () => {
            this._refresh();
            return true;
        });
    }

    _run(argv) {
        try {
            let proc = new Gio.Subprocess({
                argv: argv,
                flags: Gio.SubprocessFlags.STDOUT_PIPE | Gio.SubprocessFlags.STDERR_SILENCE
            });
            proc.init(null);
            let result = proc.communicate_utf8(null, null);
            return proc.get_successful() ? result[1] : '';
        } catch (e) {
            global.logError(e);
            return '';
        }
    }

    _refresh() {
        let demo = GLib.build_filenamev([GLib.get_home_dir(), '.config', 'ros', 'power-tree-demo']);
        let pct = -1;
        let charging = false;
        let origin = 'Kein Akku erkannt';

        if (GLib.file_test(demo, GLib.FileTest.EXISTS)) {
            let value = this._run(['/usr/bin/cat', demo]).trim();
            let m = value.match(/^(\d{1,3})(?:\s+(charging))?$/);
            if (m) {
                pct = Math.max(0, Math.min(100, Number(m[1])));
                charging = Boolean(m[2]);
                origin = 'DEMO';
            }
        } else {
            let devices = this._run(['/usr/bin/upower', '-e']).split('\n')
                .filter(x => /\/battery_[^/]+$/.test(x));
            if (devices.length > 0) {
                let info = this._run(['/usr/bin/upower', '-i', devices[0]]);
                let m = info.match(/^\s*percentage:\s*(\d+(?:\.\d+)?)%/m);
                let state = info.match(/^\s*state:\s*(\S+)/m);
                if (m) {
                    pct = Math.max(0, Math.min(100, Math.round(Number(m[1]))));
                    charging = Boolean(state && state[1] === 'charging');
                    origin = 'UPower';
                }
            }
        }

        let graphic = pct >= 0 ? pct : 0;
        let suffix = charging ? '-charging' : '';
        this.set_applet_icon_path(`${this._path}/icons/tree-${graphic}${suffix}.svg`);
        // Percent is visible in the panel, not only as tooltip.
        this.set_applet_label(pct < 0 ? '—' : `${pct}%`);
        this.set_applet_tooltip(pct < 0
            ? 'ROS Power Tree: kein Akku erkannt – Demo optional'
            : `ROS Power Tree: ${pct}%${charging ? ' · lädt' : ''} (${origin})`);
    }

    on_applet_clicked() { this._refresh(); }
    on_applet_removed_from_panel() {
        if (this._timer) Mainloop.source_remove(this._timer);
        this._timer = 0;
    }
}
function main(metadata, orientation, panelHeight, instanceId) {
    return new RosPowerTree(metadata, orientation, panelHeight, instanceId);
}
