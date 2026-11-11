#!/usr/bin/python3
"""Designs 1.1 — ROS Cinnamon theme selector (GTK 3)."""
import subprocess
import sys
from pathlib import Path

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk, GLib, GdkPixbuf
except (ImportError, ValueError) as exc:
    print('GTK 3 / python3-gi fehlt:', exc, file=sys.stderr)
    sys.exit(2)

HOME = Path.home()
THEME_CLI = HOME / '.local/bin/ros-theme'
ASSETS = Path(__file__).resolve().parent / 'assets'
THEMES = [
    ('Dark', 'ROS Dark', 'Der ROS-Klassiker', '#80F0A9', '#0B1911'),
    ('Gaming', 'ROS Gaming', 'Für Gaming und Unterhaltung', '#B18CFF', '#24163B'),
    ('IT', 'ROS IT', 'Für Administration und Entwicklung', '#59E3E7', '#0C3135'),
    ('Creator', 'ROS Creator', 'Für Medien und Kreativität', '#F5BE67', '#382714'),
    ('Stealth', 'ROS Stealth', 'Dezent und konzentriert', '#A2C1B2', '#252E2B'),
    ('Nordic', 'ROS Nordic', 'Klar und nordisch', '#8ABFFF', '#172A40'),
]


def active_theme():
    try:
        res = subprocess.run(['gsettings', 'get', 'org.cinnamon.theme', 'name'],
                             capture_output=True, text=True, timeout=5, check=True)
        value = res.stdout.strip().strip("'\"")
        return value.removeprefix('ROS-')
    except (OSError, subprocess.SubprocessError):
        return None


class Designs(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title='Designs')
        self.set_default_size(840, 680)
        self.set_size_request(610, 480)
        self.set_position(Gtk.WindowPosition.CENTER)
        self._style()
        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(self.root)
        top = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        top.get_style_context().add_class('header')
        self.root.pack_start(top, False, False, 0)
        title_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        top.pack_start(title_box, True, True, 0)
        heading = Gtk.Label(label='Designs', xalign=0)
        heading.get_style_context().add_class('main-heading')
        title_box.pack_start(heading, False, False, 0)
        subtitle = Gtk.Label(label='Wähle dein ROS-Design – alle Einstellungen bleiben erhalten.', xalign=0)
        subtitle.get_style_context().add_class('muted')
        title_box.pack_start(subtitle, False, False, 0)

        self.status = Gtk.Label(label='', xalign=0)
        self.status.get_style_context().add_class('status')
        self.root.pack_start(self.status, False, False, 0)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.root.pack_start(scroll, True, True, 0)
        container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        container.set_margin_top(18)
        container.set_margin_bottom(18)
        container.set_margin_start(20)
        container.set_margin_end(20)
        scroll.add(container)
        self.grid = Gtk.Grid(column_spacing=16, row_spacing=16)
        self.grid.set_column_homogeneous(True)
        container.pack_start(self.grid, False, False, 0)
        self.cards = {}
        for index, (key, name, description, accent, bg) in enumerate(THEMES):
            card = Gtk.Button()
            card.get_style_context().add_class('theme-card')
            card.set_relief(Gtk.ReliefStyle.NONE)
            card.connect('clicked', self._apply, key)
            inside = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            inside.set_margin_top(12)
            inside.set_margin_bottom(12)
            inside.set_margin_start(12)
            inside.set_margin_end(12)
            card.add(inside)
            image = Gtk.Image.new_from_file(str(ASSETS / f'{key}.png'))
            image.set_hexpand(True)
            inside.pack_start(image, False, False, 0)
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            inside.pack_start(row, False, False, 0)
            label = Gtk.Label(label=name, xalign=0)
            label.get_style_context().add_class('card-name')
            row.pack_start(label, True, True, 0)
            marker = Gtk.Label(label='')
            marker.get_style_context().add_class('active-badge')
            row.pack_end(marker, False, False, 0)
            desc = Gtk.Label(label=description, xalign=0)
            desc.get_style_context().add_class('muted')
            inside.pack_start(desc, False, False, 0)
            self.cards[key] = (card, marker)
            self.grid.attach(card, index % 2, index // 2, 1, 1)
        footer = Gtk.Label(label='Klicke auf eine Vorschau, um das Design anzuwenden.\nPower Tree und ROS-Icons bleiben unverändert.', xalign=0)
        footer.get_style_context().add_class('muted')
        container.pack_start(footer, False, False, 0)
        self._refresh()
        self.show_all()

    def _style(self):
        css = b'''\n        window {background-color: #0C1510; color: #EBF7EF;}\n        .header {background-color: #13231A; padding: 24px 26px; border-bottom: 1px solid #294536;}\n        .main-heading {font-size: 26px; font-weight: 700; color: #96EDB2;}\n        .muted {color: #AABFB1; font-size: 12px;}\n        .status {padding: 10px 22px; color: #96EDB2;}\n        .theme-card {background-color: #14221A; border: 1px solid #355141; border-radius: 12px; padding: 0;}\n        .theme-card:hover {background-color: #1A3023; border-color: #8FE6AD;}\n        .theme-card.active {border: 2px solid #96EDB2;}\n        .card-name {font-size: 16px; font-weight: 600; color: #F0FFF3;}\n        .active-badge {font-size: 11px; color: #96EDB2;}\n        '''
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def _refresh(self):
        current = active_theme()
        for key, (card, label) in self.cards.items():
            context = card.get_style_context()
            if key == current:
                context.add_class('active')
                label.set_text('✓ Aktiv')
            else:
                context.remove_class('active')
                label.set_text('')
        self.status.set_text(f'Aktuelles Design: ROS {current}' if current else 'Aktuelles Design konnte nicht ermittelt werden.')

    def _apply(self, _button, key):
        if key == active_theme():
            self.status.set_text(f'ROS {key} ist bereits aktiv.')
            return
        if not THEME_CLI.is_file():
            self._error('Die ROS-Themeverwaltung fehlt: ~/.local/bin/ros-theme')
            return
        try:
            result = subprocess.run([str(THEME_CLI), 'apply', key],
                                    text=True, capture_output=True, timeout=25)
        except (OSError, subprocess.TimeoutExpired) as exc:
            self._error(str(exc))
            return
        if result.returncode != 0:
            self._error((result.stderr or result.stdout or 'Unbekannter Fehler').strip())
            return
        self._refresh()
        self.status.set_text(f'ROS {key} aktiviert. Falls nötig, einmal grafisch ab- und anmelden.')

    def _error(self, message):
        dialog = Gtk.MessageDialog(transient_for=self, flags=0,
            message_type=Gtk.MessageType.ERROR, buttons=Gtk.ButtonsType.CLOSE,
            text='Design konnte nicht angewendet werden')
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()


class App(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='de.ros.designs')

    def do_activate(self):
        window = self.get_active_window()
        if window is None:
            window = Designs(self)
        window.present()


if __name__ == '__main__':
    sys.exit(App().run(sys.argv))
