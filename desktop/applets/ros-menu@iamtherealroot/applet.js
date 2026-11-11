/* ROS Menu 1.0 preview — independent Cinnamon applet, no Mint menu code copied. */
const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const Main = imports.ui.main;
const Util = imports.misc.util;
const Gio = imports.gi.Gio;
const St = imports.gi.St;
const Clutter = imports.gi.Clutter;

const SECTIONS = [
    ['Alle', null],
    ['Internet', 'Network'],
    ['Büro', 'Office'],
    ['Entwicklung', 'Development'],
    ['Grafik', 'Graphics'],
    ['Multimedia', 'AudioVideo'],
    ['Spiele', 'Game'],
    ['System', 'System'],
    ['Zubehör', 'Utility']
];
const FAVORITES = [
    'nemo.desktop', 'firefox.desktop', 'ros-terminal.desktop'
];

class ROSMenu extends Applet.TextIconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this._metadata = metadata;
        this._category = null;
        this._apps = [];
        this._maxRows = 80;
        this.set_applet_tooltip('ROS Menu — Sei wie Root!');
        this.set_applet_icon_path(metadata.path + '/tree.svg');
        this.set_applet_label('');

        this.menuManager = new PopupMenu.PopupMenuManager(this);
        this.menu = new Applet.AppletPopupMenu(this, orientation);
        this.menuManager.addMenu(this.menu);
        this._build();
        this._refreshApps();
        this._showApps();
    }

    _heading(text) {
        const label = new PopupMenu.PopupMenuItem(text, { reactive: false });
        label.actor.style = 'font-weight: bold; color: #98edb5;';
        this.menu.addMenuItem(label);
    }

    _build() {
        this.menu.actor.style = 'min-width: 440px; background-color: #101d16; color: #eaf8ee;';
        this._heading('ROS  ·  Sei wie Root!');
        const inputItem = new PopupMenu.PopupBaseMenuItem({ reactive: false });
        this._search = new St.Entry({
            hint_text: 'Programme suchen …',
            can_focus: true,
            track_hover: true,
            style: 'width: 410px; padding: 10px; background-color: #203429; color: #f1fff4; border: 1px solid #416b51; border-radius: 8px;'
        });
        inputItem.addActor(this._search);
        this.menu.addMenuItem(inputItem);
        this._search.get_clutter_text().connect('text-changed', () => this._showApps());

        this._categories = new PopupMenu.PopupSubMenuMenuItem('Kategorien');
        this.menu.addMenuItem(this._categories);
        for (let [title, category] of SECTIONS) {
            let item = new PopupMenu.PopupMenuItem(title);
            item.connect('activate', () => {
                this._category = category;
                this._search.set_text('');
                this._showApps();
            });
            this._categories.menu.addMenuItem(item);
        }

        this._heading('Anwendungen');
        this._results = new PopupMenu.PopupMenuSection();
        this.menu.addMenuItem(this._results);
        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        const quick = new PopupMenu.PopupSubMenuMenuItem('Favoriten');
        this.menu.addMenuItem(quick);
        for (let id of FAVORITES) {
            let item = new PopupMenu.PopupMenuItem(id.replace('.desktop', ''));
            item.connect('activate', () => this._launchId(id));
            quick.menu.addMenuItem(item);
        }
        const session = new PopupMenu.PopupSubMenuMenuItem('Sitzung & Energie');
        this.menu.addMenuItem(session);
        for (let [text, command] of [
            ['Bildschirm sperren', 'cinnamon-screensaver-command --lock'],
            ['Abmelden', 'cinnamon-session-quit --logout'],
            ['Neustarten', 'cinnamon-session-quit --reboot'],
            ['Herunterfahren', 'cinnamon-session-quit --power-off']
        ]) {
            let item = new PopupMenu.PopupMenuItem(text);
            item.connect('activate', () => {
                this.menu.close();
                Util.spawnCommandLine(command);
            });
            session.menu.addMenuItem(item);
        }
    }

    _refreshApps() {
        this._apps = Gio.AppInfo.get_all().filter(app => app.should_show());
        this._apps.sort((a, b) => a.get_display_name().localeCompare(b.get_display_name()));
    }

    _launchId(id) {
        const found = this._apps.find(app => app.get_id() === id);
        if (!found)
            return;
        this._launch(found);
    }

    _launch(app) {
        this.menu.close();
        try {
            app.launch([], null);
        } catch (e) {
            global.logError(e);
        }
    }

    _showApps() {
        if (!this._results)
            return;
        this._results.removeAll();
        const term = this._search.get_text().toLocaleLowerCase().trim();
        let visible = 0;
        for (let app of this._apps) {
            const name = app.get_display_name() || '';
            const description = app.get_description() || '';
            const categories = (app.get_categories && app.get_categories()) || '';
            if (this._category && !categories.split(';').includes(this._category))
                continue;
            if (term && !(name.toLocaleLowerCase().includes(term) ||
                          description.toLocaleLowerCase().includes(term)))
                continue;
            const item = new PopupMenu.PopupMenuItem(name);
            item.connect('activate', () => this._launch(app));
            this._results.addMenuItem(item);
            if (++visible >= this._maxRows)
                break;
        }
        if (!visible)
            this._results.addMenuItem(new PopupMenu.PopupMenuItem('Keine Anwendungen gefunden', { reactive: false }));
    }

    on_applet_clicked() {
        if (!this.menu.isOpen) {
            this._refreshApps();
            this._showApps();
        }
        this.menu.toggle();
    }
}

function main(metadata, orientation, panelHeight, instanceId) {
    return new ROSMenu(metadata, orientation, panelHeight, instanceId);
}
