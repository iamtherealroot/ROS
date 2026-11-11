/* ROS Menu 1.5.5 preview — Cinnamon 6.6, aligned launcher. */
const Applet = imports.ui.applet;
const PopupMenu = imports.ui.popupMenu;
const Util = imports.misc.util;
const Gio = imports.gi.Gio;
const St = imports.gi.St;
const Clutter = imports.gi.Clutter;
const Pango = imports.gi.Pango;
const GLib = imports.gi.GLib;

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
        this._categoryChangedAt = 0;
        this._categoryRefreshId = 0;
        this._suspendSearchRefresh = false;
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
        // Compact vertical launcher: search, shortcuts, categories, programs, power.
        this.menu.actor.style = 'background-color: #101d16; color: #f0fff3; min-width: 505px;';
        this._heading('ROS   ·   Sei wie Root!');

        const searchRow = new PopupMenu.PopupBaseMenuItem({reactive: false});
        this._search = new St.Entry({
            hint_text: 'Programm oder Einstellung suchen …',
            can_focus: true,
            track_hover: true,
            style: 'width: 465px; padding: 10px; background-color: #203429; color: #ffffff; border: 1px solid #5c9871; border-radius: 8px;'
        });
        searchRow.addActor(this._search);
        this.menu.addMenuItem(searchRow);
        this._search.get_clutter_text().connect('text-changed', () => {
            if (!this._suspendSearchRefresh)
                this._showApps();
        });

        // Favorites are always visible as compact, one-click shortcuts.
        const favoriteRow = new PopupMenu.PopupBaseMenuItem({reactive: false});
        const favoriteBox = new St.BoxLayout({
            vertical: false,
            style: 'spacing: 8px; padding: 2px 2px 5px 2px;'
        });
        for (const [title, id, icon] of [
            ['Dateien', 'nemo.desktop', 'folder-symbolic'],
            ['Firefox', 'firefox.desktop', 'web-browser-symbolic'],
            ['Terminal', 'ros-terminal.desktop', 'utilities-terminal-symbolic']
        ]) {
            const button = new St.Button({
                reactive: true, can_focus: true, track_hover: true,
                style: 'width: 136px; padding: 8px 9px; border-radius: 6px; background-color: #234631;'
            });
            const inside = new St.BoxLayout({vertical: false, style: 'spacing: 7px;'});
            const favoriteApp = Gio.DesktopAppInfo.new(id);
            const appIcon = favoriteApp && favoriteApp.get_icon();
            inside.add_child(appIcon ? new St.Icon({gicon: appIcon, icon_size: 19}) : this._makeIcon(icon, 19));
            inside.add_child(new St.Label({text: title, y_align: 2, style: 'color: #ffffff;'}));
            button.set_child(inside);
            button.connect('clicked', () => this._launchId(id));
            favoriteBox.add_child(button);
        }
        favoriteRow.addActor(favoriteBox);
        this.menu.addMenuItem(favoriteRow);

        const categoryItem = new PopupMenu.PopupBaseMenuItem({reactive: false});
        const categoryGrid = new St.BoxLayout({vertical: true, style: 'spacing: 3px; padding: 3px 2px 4px 2px;'});
        // Three even columns are easier to scan than a long left sidebar.
        for (let index = 0; index < SECTIONS.length; index += 3) {
            const row = new St.BoxLayout({vertical: false, style: 'spacing: 5px;'});
            for (const [title, category, icon] of SECTIONS.slice(index, index + 3)) {
                const button = new St.Button({
                    reactive: true, can_focus: true, track_hover: true,
                    style: 'width: 136px; padding: 7px 7px; border-radius: 6px;'
                });
                const contents = new St.BoxLayout({vertical: false, style: 'spacing: 6px;'});
                contents.add_child(this._makeIcon(icon, 16));
                contents.add_child(new St.Label({text: title, y_align: 2, style: 'color: #ffffff;'}));
                button.set_child(contents);
                button.connect('clicked', () => {
                    // Don't create new application buttons during the same
                    // pointer-click sequence. It previously launched unrelated
                    // programs (Calculator / Bluetooth) on category selection.
                    this._categoryChangedAt = GLib.get_monotonic_time();
                    this._category = category;
                    if (this._categoryRefreshId) {
                        GLib.source_remove(this._categoryRefreshId);
                        this._categoryRefreshId = 0;
                    }
                    this._suspendSearchRefresh = true;
                    this._search.set_text('');
                    this._suspendSearchRefresh = false;
                    for (const child of this._appList.get_children())
                        child.destroy();
                    this._resultsTitle.text = title;
                    this._categoryRefreshId = GLib.timeout_add(
                        GLib.PRIORITY_DEFAULT, 350, () => {
                            this._categoryRefreshId = 0;
                            this._showApps();
                            return GLib.SOURCE_REMOVE;
                        }
                    );
                });
                row.add_child(button);
                this._categoryButtons.push([category, button]);
            }
            categoryGrid.add_child(row);
        }
        categoryItem.addActor(categoryGrid);
        this.menu.addMenuItem(categoryItem);

        // Full-width list of programs; the search remains visible above.
        const resultsRow = new PopupMenu.PopupBaseMenuItem({reactive: false});
        // Retain Cinnamon's normal left padding: align the grid with the search
        // and the footer rather than the menu's outside border.
        const resultsBox = new St.BoxLayout({
            vertical: true, x_align: Clutter.ActorAlign.START,
            style: 'width: 485px; padding: 0 2px;'
        });
        this._resultsTitle = new St.Label({
            text: 'Alle Programme',
            style: 'font-weight: bold; color: #98edb5; padding: 5px 7px;'
        });
        resultsBox.add_child(this._resultsTitle);
        const scroll = new St.ScrollView({
            style: 'width: 485px; min-height: 145px; max-height: 190px;',
            x_fill: true, y_fill: true
        });
        // Keep mouse-wheel/touch scrolling while hiding both scrollbar tracks.
        scroll.set_policy(St.PolicyType.NEVER, St.PolicyType.NEVER);
        this._appList = new St.BoxLayout({
            vertical: true, x_expand: false, x_align: Clutter.ActorAlign.START,
            style: 'width: 480px; spacing: 5px;'
        });
        scroll.add_actor(this._appList);
        resultsBox.add_child(scroll);
        resultsRow.addActor(resultsBox);
        this.menu.addMenuItem(resultsRow);

        this.menu.addMenuItem(new PopupMenu.PopupSeparatorMenuItem());

        const powerRow = new PopupMenu.PopupBaseMenuItem({reactive: false});
        const powerBox = new St.BoxLayout({
            vertical: false,
            x_expand: true, x_align: Clutter.ActorAlign.FILL,
            style: 'width: 465px; spacing: 6px; padding: 3px 0px 2px 0px;'
        });
        for (const [title, icon, command, background, foreground] of [
            ['Sperren', 'system-lock-screen-symbolic', 'cinnamon-screensaver-command --lock', '#304957', '#e2f3ff'],
            ['Abmelden', 'system-log-out-symbolic', 'cinnamon-session-quit --logout', '#645320', '#fff1ae'],
            ['Neustart', 'view-refresh-symbolic', 'cinnamon-session-quit --reboot', '#78441e', '#ffe1bd'],
            ['Ausschalten', 'system-shutdown-symbolic', 'cinnamon-session-quit --power-off', '#773034', '#ffe0e0']
        ]) {
            const button = new St.Button({
                reactive: true, can_focus: true, track_hover: true,
                x_expand: false, x_align: Clutter.ActorAlign.START,
                style: 'width: 108px; padding: 9px 3px; border-radius: 6px; background-color: ' + background + '; color: ' + foreground + ';'
            });
            const contents = new St.BoxLayout({
                vertical: false, x_align: Clutter.ActorAlign.CENTER,
                style: 'spacing: 4px;'
            });
            const actionIcon = this._makeIcon(icon, 14);
            actionIcon.style = 'color: ' + foreground + ';';
            contents.add_child(actionIcon);
            contents.add_child(new St.Label({
                text: title, y_align: Clutter.ActorAlign.CENTER,
                style: 'color: ' + foreground + ';'
            }));
            button.set_child(contents);
            button.connect('clicked', () => {
                this.menu.close();
                Util.spawnCommandLine(command);
            });
            powerBox.add_child(button);
        }
        powerRow.addActor(powerBox);
        this.menu.addMenuItem(powerRow);
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
        // Some Cinnamon popup event paths can deliver a click to a freshly
        // rebuilt application tile immediately after choosing a category.
        // A deliberate second click still launches the chosen application.
        if (GLib.get_monotonic_time() - this._categoryChangedAt < 1100000)
            return;
        this.menu.close();
        try {
            app.launch([], null);
        } catch (e) {
            global.logError(e);
        }
    }

    _appCategories(app) {
        // Gio.AppInfo.get_all() can return Gio.AppInfo implementations with
        // no get_categories(). Obtain freedesktop categories from the desktop
        // launcher when possible. Never infer categories from displayed names.
        try {
            if (typeof app.get_categories === 'function')
                return (app.get_categories() || '').split(';').filter(Boolean);
            const id = app.get_id();
            const desktop = id ? Gio.DesktopAppInfo.new(id) : null;
            if (desktop)
                return (desktop.get_categories() || '').split(';').filter(Boolean);
        } catch (e) {
            global.logError(e);
        }
        return [];
    }

    _matchesCategory(categories, selected) {
        const aliases = {
            'Network': ['Network', 'WebBrowser', 'Email', 'InstantMessaging'],
            'Office': ['Office'],
            'Development': ['Development', 'IDE', 'GUIDesigner'],
            'Graphics': ['Graphics', 'Photography', '2DGraphics', '3DGraphics'],
            'AudioVideo': ['AudioVideo', 'Audio', 'Video', 'Player', 'Recorder'],
            'Game': ['Game'],
            'System': ['System', 'Settings', 'Security'],
            'Utility': ['Utility', 'Accessories', 'Calculator', 'TextEditor']
        };
        return (aliases[selected] || [selected]).some(tag => categories.includes(tag));
    }

    _showApps() {
        if (!this._appList)
            return;
        if (this._categoryRefreshId)
            return;
        for (const child of this._appList.get_children())
            child.destroy();

        const term = this._search.get_text().toLocaleLowerCase().trim();
        const selected = SECTIONS.find(row => row[1] === this._category);
        this._resultsTitle.text = term ? 'Suchergebnisse' : (selected ? selected[0] : 'Alle Programme');
        for (const [key, button] of this._categoryButtons) {
            button.style = key === this._category
                ? 'width: 136px; padding: 7px 7px; border-radius: 6px; background-color: #305a3c; color: #ffffff;'
                : 'width: 136px; padding: 7px 7px; border-radius: 6px; color: #d8e9dd;';
        }

        // Two evenly sized columns with translucent glass-like application tiles.
        // Long names are truncated to keep the grid aligned.
        const visible = this._apps.filter(app => {
            const name = app.get_display_name() || '';
            const description = app.get_description() || '';
            const categories = this._appCategories(app);
            if (!term && this._category && !this._matchesCategory(categories, this._category))
                return false;
            return !term || name.toLocaleLowerCase().includes(term) ||
                description.toLocaleLowerCase().includes(term);
        }).slice(0, this._maxRows);

        if (visible.length === 0) {
            this._appList.add_child(new St.Label({
                text: 'Keine Anwendungen gefunden',
                style: 'padding: 12px; color: #f3fff6;'
            }));
            return;
        }

        for (let i = 0; i < visible.length; i += 2) {
            const gridRow = new St.BoxLayout({
                vertical: false,
                x_align: Clutter.ActorAlign.START,
                style: 'width: 480px; spacing: 8px;'
            });
            for (const app of visible.slice(i, i + 2)) {
                const name = app.get_display_name() || '';
                const tile = new St.Button({
                    reactive: true, can_focus: true, track_hover: true,
                    x_align: Clutter.ActorAlign.START,
                    style: 'width: 218px; padding: 8px 8px; border-radius: 7px; border: none; box-shadow: none; background-color: rgba(210, 255, 224, 0.045); color: #f3fff6;'
                });
                const contents = new St.BoxLayout({
                    vertical: false, x_align: Clutter.ActorAlign.START,
                    style: 'spacing: 7px;'
                });
                const icon = app.get_icon();
                contents.add_child(icon
                    ? new St.Icon({gicon: icon, icon_size: 19})
                    : this._makeIcon('application-x-executable-symbolic', 19));
                const label = new St.Label({
                    text: name, y_align: Clutter.ActorAlign.CENTER,
                    x_align: Clutter.ActorAlign.START,
                    style: 'color: #f3fff6;'
                });
                label.clutter_text.set_ellipsize(Pango.EllipsizeMode.END);
                label.set_width(159);
                contents.add_child(label);
                tile.set_child(contents);
                tile.connect('clicked', () => this._launch(app));
                gridRow.add_child(tile);
            }
            this._appList.add_child(gridRow);
        }
    }

    on_applet_removed_from_panel() {
        if (this._categoryRefreshId) {
            GLib.source_remove(this._categoryRefreshId);
            this._categoryRefreshId = 0;
        }
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
