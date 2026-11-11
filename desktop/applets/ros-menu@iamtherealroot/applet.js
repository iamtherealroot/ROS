/* ROS Menu 1.1 — Cinnamon 6.6 desktop applet. */
const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const Util = imports.misc.util;
const Gio = imports.gi.Gio;
const St = imports.gi.St;

const SECTIONS = [
    ['Alle Programme', null, 'view-grid-symbolic'],
    ['Internet', 'Network', 'network-workgroup-symbolic'],
    ['Büro', 'Office', 'x-office-document-symbolic'],
    ['Entwicklung', 'Development', 'applications-development-symbolic'],
    ['Grafik', 'Graphics', 'applications-graphics-symbolic'],
    ['Multimedia', 'AudioVideo', 'applications-multimedia-symbolic'],
    ['Spiele', 'Game', 'applications-games-symbolic'],
    ['System', 'System', 'applications-system-symbolic'],
    ['Zubehör', 'Utility', 'applications-utilities-symbolic']
];
const FAVORITES = ['nemo.desktop', 'firefox.desktop', 'ros-terminal.desktop'];

class ROSMenu extends Applet.TextIconApplet {
    constructor(metadata, orientation, panelHeight, instanceId) {
        super(orientation, panelHeight, instanceId);
        this._category = null;
        this._apps = [];
        this._maxRows = 120;
        this._categoryButtons = [];
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
        label.actor.style = 'font-weight: bold; color: #98edb5; padding: 7px 9px;';
        this.menu.addMenuItem(label);
    }

    _makeIcon(icon, size = 18) {
        return new St.Icon({ icon_name: icon, icon_size: size });
    }

    _build() {
        this.menu.actor.style = 'background-color: #101d16; color: #eaf8ee; min-width: 640px;';
        this._heading('ROS  ·  Sei wie Root!');

        const searchRow = new PopupMenu.PopupBaseMenuItem({reactive: false});
        this._search = new St.Entry({
            hint_text: 'Anwendungen suchen …',
            can_focus: true,
            track_hover: true,
            style: 'width: 590px; padding: 9px; background-color: #203429; color: #f1fff4; border: 1px solid #416b51; border-radius: 7px;'
        });
        searchRow.addActor(this._search);
        this.menu.addMenuItem(searchRow);
        this._search.get_clutter_text().connect('text-changed', () => this._showApps());

        const contentRow = new PopupMenu.PopupBaseMenuItem({reactive: false});
        const columns = new St.BoxLayout({vertical: false, style: 'spacing: 12px; padding: 5px 6px;'});
        const categories = new St.BoxLayout({
            vertical: true,
            style: 'width: 180px; spacing: 2px; padding-right: 9px; border-right: 1px solid #416b51;'
        });
        for (const [label, key, icon] of SECTIONS) {
            const button = new St.Button({
                reactive: true, can_focus: true, track_hover: true,
                style: 'padding: 8px 6px; border-radius: 6px;'
            });
            const inner = new St.BoxLayout({vertical: false, style: 'spacing: 8px;'});
            inner.add_child(this._makeIcon(icon));
            inner.add_child(new St.Label({text: label, y_align: 2}));
            button.set_child(inner);
            button.connect('clicked', () => {
                this._category = key;
                this._search.set_text('');
                this._showApps();
            });
            categories.add_child(button);
            this._categoryButtons.push([key, button]);
        }
        columns.add_child(categories);

        const right = new St.BoxLayout({vertical: true, style: 'width: 390px;'});
        this._resultsTitle = new St.Label({
            text: 'Alle Programme',
            style: 'font-weight: bold; color: #98edb5; padding: 6px;'
        });
        right.add_child(this._resultsTitle);
        const scroll = new St.ScrollView({
            style: 'max-height: 390px; min-height: 270px; width: 390px;',
            x_fill: true,
            y_fill: true
        });
        this._appList = new St.BoxLayout({vertical: true, style: 'spacing: 2px;'});
        scroll.add_actor(this._appList);
        right.add_child(scroll);
        columns.add_child(right);
        contentRow.addActor(columns);
        this.menu.addMenuItem(contentRow);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());
        const favorites = new PopupMenu.PopupSubMenuMenuItem('Favoriten');
        this.menu.addMenuItem(favorites);
        for (const id of FAVORITES) {
            const item = new PopupMenu.PopupMenuItem(id.replace('.desktop', ''));
            item.connect('activate', () => this._launchId(id));
            favorites.menu.addMenuItem(item);
        }
        const session = new PopupMenu.PopupSubMenuMenuItem('Sitzung & Energie');
        this.menu.addMenuItem(session);
        for (const [title, command] of [
            ['Bildschirm sperren', 'cinnamon-screensaver-command --lock'],
            ['Abmelden', 'cinnamon-session-quit --logout'],
            ['Neustarten', 'cinnamon-session-quit --reboot'],
            ['Herunterfahren', 'cinnamon-session-quit --power-off']
        ]) {
            const item = new PopupMenu.PopupMenuItem(title);
            item.connect('activate', () => {
                this.menu.close();
                Util.spawnCommandLine(command);
            });
            session.menu.addMenuItem(item);
        }
    }

    _refreshApps() {
        this._apps = Gio.AppInfo.get_all().filter(app => app.should_show());
        this._apps.sort((a, b) =>
            (a.get_display_name() || '').localeCompare(b.get_display_name() || ''));
    }

    _launchId(id) {
        const app = this._apps.find(a => a.get_id() === id);
        if (app)
            this._launch(app);
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
        if (!this._appList)
            return;
        for (const child of this._appList.get_children())
            child.destroy();

        const term = this._search.get_text().toLocaleLowerCase().trim();
        const selected = SECTIONS.find(row => row[1] === this._category);
        this._resultsTitle.text = term ? 'Suchergebnisse' : (selected ? selected[0] : 'Alle Programme');
        for (const [key, button] of this._categoryButtons) {
            button.style = key === this._category
                ? 'padding: 8px 6px; border-radius: 6px; background-color: #305a3c; color: #ffffff;'
                : 'padding: 8px 6px; border-radius: 6px; color: #d8e9dd;';
        }

        let count = 0;
        for (const app of this._apps) {
            const name = app.get_display_name() || '';
            const description = app.get_description() || '';
            const categories = (app.get_categories && app.get_categories()) || '';
            if (!term && this._category && !categories.split(';').includes(this._category))
                continue;
            if (term && !(name.toLocaleLowerCase().includes(term) ||
                        description.toLocaleLowerCase().includes(term)))
                continue;
            const button = new St.Button({
                reactive: true, can_focus: true, track_hover: true,
                style: 'padding: 7px 8px; border-radius: 5px;'
            });
            const row = new St.BoxLayout({vertical: false, style: 'spacing: 9px;'});
            const icon = app.get_icon();
            if (icon)
                row.add_child(new St.Icon({gicon: icon, icon_size: 20}));
            else
                row.add_child(this._makeIcon('application-x-executable-symbolic', 20));
            row.add_child(new St.Label({text: name, y_align: 2}));
            button.set_child(row);
            button.connect('clicked', () => this._launch(app));
            this._appList.add_child(button);
            if (++count >= this._maxRows)
                break;
        }
        if (!count)
            this._appList.add_child(new St.Label({text: 'Keine Anwendungen gefunden',
                                                  style: 'padding: 12px;'}));
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
