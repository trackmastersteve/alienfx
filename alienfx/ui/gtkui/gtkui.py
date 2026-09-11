#
# gtkui.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2026 Track Master Steve <trackmastersteve@gmail.com>
#
# Alienfx is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Alienfx is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with alienfx.    If not, write to:
#   The Free Software Foundation, Inc.,
#   51 Franklin Street, Fifth Floor
#   Boston, MA  02110-1301, USA.
#

"""GTK4 GUI interface to alienfx."""

import argparse
import logging
import os
import subprocess
import sys
import threading
import time

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from alienfx.core.prober import AlienFXProber
from alienfx.core.themefile import AlienFXThemeFile
from alienfx.ui.gtkui.action_renderer import AlienFXActions
from alienfx.ui.gtkui.colour_palette import ColourPalette


class AlienFXApp(Gtk.Application):
    application_id = "io.github.trackmastersteve.alienfx"
    colours = [
        "#000000", "#FFFFFF", "#00F3F1", "#00F89A", "#00FA52", "#00FF00",
        "#79F900", "#C1F800", "#F0E500", "#FF4500", "#FF0000", "#FF006F",
        "#FF00B1", "#FF00F5", "#A400F5", "#6500F6", "#0000FF", "#004BF5",
        "#009AF4",
    ]

    def __init__(self, root_mode=False):
        super().__init__(application_id=self.application_id)
        GLib.set_prgname("alienfx")
        GLib.set_application_name("AlienFX")
        self.connect("activate", self.on_activate)
        self.root_mode = root_mode or os.geteuid() == 0
        self.controller = AlienFXProber.get_controller()
        self.themefile = AlienFXThemeFile(self.controller)
        self.action_type = self.themefile.KW_ACTION_TYPE_FIXED
        self.selected_action = None
        self.theme_edited = False
        self.apply_error = None
        self.set_theme_done = True
        self.apply_started_at = None

    def _button(self, label, callback):
        button = Gtk.Button(label=label)
        button.connect("clicked", callback)
        return button

    def _message(self, message):
        alert = Gtk.AlertDialog()
        alert.set_message(message)
        alert.show(self.window)

    def _set_status(self, message):
        self.status_label.set_text(message)

    def _make_row(self, zone, actions):
        row = Gtk.ListBoxRow()
        row.zone = zone
        box = Gtk.Box(spacing=8)
        box.set_margin_start(6); box.set_margin_end(6)
        box.set_margin_top(4); box.set_margin_bottom(4)
        box.append(Gtk.Label(label=zone, xalign=0))
        action_box = Gtk.Box(spacing=3)
        for index, action in enumerate(actions.actions):
            button = Gtk.Button(label=AlienFXThemeFile.get_action_type(action))
            button.connect("clicked", self._select_action, zone, index)
            action_box.append(button)
        box.append(action_box)
        row.set_child(box)
        return row

    def _select_action(self, _button, zone, index):
        self.selected_action = (zone, index)
        self.properties.set_sensitive(True)
        self.delete_button.set_sensitive(len(self._row_data(zone)[1].actions) > 1)

    def _row_data(self, zone):
        return next(item for item in self.current_rows if item[0] == zone)

    def _set_rows(self, rows):
        self.current_rows = rows
        while child := self.zone_list.get_first_child():
            self.zone_list.remove(child)
        for zone, actions in rows:
            self.zone_list.append(self._make_row(zone, actions))

    def _normal_rows(self):
        rows = []
        states = (
            self.controller.ZONE_LEFT_KEYBOARD, self.controller.ZONE_MIDDLE_LEFT_KEYBOARD,
            self.controller.ZONE_MIDDLE_RIGHT_KEYBOARD, self.controller.ZONE_RIGHT_KEYBOARD,
            self.controller.ZONE_RIGHT_SPEAKER, self.controller.ZONE_LEFT_SPEAKER,
            self.controller.ZONE_ALIEN_HEAD, self.controller.ZONE_LEFT_SIDE, self.controller.ZONE_LOGO,
            self.controller.ZONE_TOUCH_PAD, self.controller.ZONE_MEDIA_BAR, self.controller.ZONE_STATUS_LEDS,
            self.controller.ZONE_POWER_BUTTON, self.controller.ZONE_HDD_LEDS,
            self.controller.ZONE_RIGHT_DISPLAY, self.controller.ZONE_LEFT_DISPLAY,
        )
        for zone in states:
            if zone in self.controller.power_zones:
                actions = AlienFXActions()
                actions.actions = self.themefile.get_zone_actions(self.controller.STATE_BOOT, zone)
                rows.append((zone, actions))
        return rows

    def _power_rows(self):
        rows = []
        for zone in self.controller.zone_map:
            if zone not in self.controller.power_zones:
                continue
            for state in self.controller.state_map:
                actions = AlienFXActions()
                actions.actions = self.themefile.get_zone_actions(state, zone)
                rows.append((state, actions))
        return rows

    def load_theme(self, theme_name=None):
        if not self.controller:
            return
        self.normal_rows = self._normal_rows()
        self.power_rows = self._power_rows()
        self._set_rows(self.normal_rows)
        self.window.set_title((theme_name or self.themefile.theme_name or "New theme") + " - Alien FX")
        self.properties.set_sensitive(False)
        self.selected_action = None

    def set_theme_dirty(self, dirty):
        self.theme_edited = dirty
        title = (self.window.get_title() or "Alien FX").lstrip("*")
        self.window.set_title(("*" if dirty else "") + title)

    def on_new_theme(self, _button):
        self.themefile = AlienFXThemeFile(self.controller)
        self.themefile.set_default_theme()
        self.load_theme("New Theme")
        self.set_theme_dirty(False)
        self.delete_theme_button.set_sensitive(False)

    def on_open_theme(self, _button):
        dialog = Gtk.Window(title="Open a theme", transient_for=self.window, modal=True)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        box.set_margin_start(12); box.set_margin_end(12); box.set_margin_top(12); box.set_margin_bottom(12)
        themes = Gtk.ListBox()
        for name in self.themefile.get_themes():
            themes.append(Gtk.Label(label=name, xalign=0))
        box.append(themes)
        def load(_button):
            row = themes.get_selected_row()
            if row:
                self.themefile.load(row.get_child().get_text())
                self.load_theme()
                self.set_theme_dirty(False)
                dialog.close()
        box.append(self._button("Open", load))
        dialog.set_child(box); dialog.present()

    def on_save_theme(self, _button):
        if self.themefile.theme_name:
            self.themefile.save(self.themefile.theme_name)
            self.set_theme_dirty(False)

    def on_delete_theme(self, _button):
        if self.themefile.delete_theme_from_disk():
            self.on_new_theme(_button)

    def on_add_action(self, _button):
        if self.selected_action is None:
            return
        zone, index = self.selected_action
        actions = self._row_data(zone)[1]
        actions.actions.insert(index + 1, self.themefile.make_zone_action(self.action_type, [[15, 15, 15]]))
        self.load_theme(); self.set_theme_dirty(True)

    def on_delete_action(self, _button):
        if self.selected_action is None:
            return
        zone, index = self.selected_action
        actions = self._row_data(zone)[1]
        if len(actions.actions) > 1:
            del actions.actions[index]
            self.load_theme(); self.set_theme_dirty(True)

    def on_colour_selected(self, swatch):
        if self.selected_action is None:
            return
        zone, index = self.selected_action
        action = self._row_data(zone)[1].actions[index]
        colours = self.themefile.get_action_colours(action) or [[0, 0, 0]]
        if self.action_type != self.themefile.KW_ACTION_TYPE_MORPH:
            colours = [colours[0]]
        self.themefile.set_action_type(action, self.action_type)
        self.themefile.set_action_colours(action, [swatch.get_colour()])
        self.set_theme_dirty(True)

    def on_apply(self, _button):
        self.toolbar.set_sensitive(False)
        self.spinner.set_visible(True); self.spinner.start()
        self._set_status("Applying theme...")
        self.set_theme_done = False; self.apply_started_at = time.monotonic()
        threading.Thread(target=self._apply_worker, daemon=True).start()
        GLib.timeout_add(100, self._apply_finished)

    def _apply_worker(self):
        try:
            if self.controller is None:
                raise RuntimeError("No AlienFX controller available")
            self.controller.set_theme(self.themefile)
            self.themefile.applied()
        except Exception as exc:
            self.apply_error = str(exc); logging.exception("Error applying theme")
        self.set_theme_done = True

    def _apply_finished(self):
        if not self.set_theme_done:
            if time.monotonic() - self.apply_started_at < 10:
                return True
            self.apply_error = "The controller timed out after 10 seconds."
            self.set_theme_done = True
        self.spinner.stop(); self.spinner.set_visible(False); self.toolbar.set_sensitive(True)
        self._set_status(self.apply_error or "Theme applied.")
        if self.apply_error:
            self._message(self.apply_error)
        return False

    def on_activate(self, _application):
        self.window = Gtk.ApplicationWindow(application=self, title="Alien FX")
        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        for margin in ("start", "end", "top", "bottom"):
            getattr(root, f"set_margin_{margin}")(8)
        self.toolbar = Gtk.Box(spacing=4)
        toolbar_items = [("New", self.on_new_theme), ("Open", self.on_open_theme),
                         ("Save", self.on_save_theme), ("Delete Theme", self.on_delete_theme),
                         ("Delete Action", self.on_delete_action), ("Add Action", self.on_add_action),
                         ("Apply", self.on_apply)]
        for label, callback in toolbar_items:
            self.toolbar.append(self._button(label, callback))
        self.delete_theme_button = self.toolbar.get_first_child().get_next_sibling().get_next_sibling().get_next_sibling()
        self.delete_button = self.delete_theme_button.get_next_sibling()
        self.add_button = self.delete_button.get_next_sibling()
        root.append(self.toolbar)
        modes = Gtk.Box(halign=Gtk.Align.CENTER, spacing=4)
        normal = Gtk.ToggleButton(label="Normal Zones"); power = Gtk.ToggleButton(label="Power Zone")
        power.set_group(normal); normal.set_active(True)
        modes.append(normal); modes.append(power); root.append(modes)
        self.zone_list = Gtk.ListBox(); self.zone_list.set_vexpand(True); root.append(self.zone_list)
        normal.connect("toggled", lambda button: button.get_active() and self._set_rows(self.normal_rows))
        power.connect("toggled", lambda button: button.get_active() and self._set_rows(self.power_rows))
        self.properties = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        fixed = Gtk.ToggleButton(label="Fixed Colour"); blink = Gtk.ToggleButton(label="Blinking Colour"); morph = Gtk.ToggleButton(label="Morphing Colour")
        blink.set_group(fixed); morph.set_group(fixed); fixed.set_active(True)
        fixed.connect("toggled", lambda button: button.get_active() and setattr(self, "action_type", self.themefile.KW_ACTION_TYPE_FIXED))
        blink.connect("toggled", lambda button: button.get_active() and setattr(self, "action_type", self.themefile.KW_ACTION_TYPE_BLINK))
        morph.connect("toggled", lambda button: button.get_active() and setattr(self, "action_type", self.themefile.KW_ACTION_TYPE_MORPH))
        types = Gtk.Box(spacing=4); types.append(fixed); types.append(blink); types.append(morph); self.properties.append(types)
        self.palette1 = ColourPalette(self.colours, 0xF, 2, 10, True, self.on_colour_selected)
        self.palette2 = ColourPalette(self.colours, 0xF, 2, 10, True, self.on_colour_selected)
        self.properties.append(self.palette1); self.properties.append(self.palette2); root.append(self.properties)
        status = Gtk.Box(spacing=6); self.status_label = Gtk.Label(xalign=0); self.spinner = Gtk.Spinner(); self.spinner.set_visible(False)
        status.append(self.status_label); status.append(self.spinner); root.append(status)
        self.window.set_child(root); self.window.present()
        if self.controller is None:
            self._message("No supported Alien FX controller found!")
            return
        self.load_theme("Current Theme" if self.themefile.load_last_theme() else "New Theme")
        self.delete_theme_button.set_sensitive(False)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root-mode", action="store_true")
    parser.add_argument("--spawn-root-ui", action="store_true")
    return parser.parse_args(argv)


def start():
    args = parse_args()
    if args.spawn_root_ui:
        subprocess.Popen([sys.executable, "-m", "alienfx.ui.gtkui.gtkui", "--root-mode"], start_new_session=True)
        return 0
    return AlienFXApp(root_mode=args.root_mode).run(None)


if __name__ == "__main__":
    raise SystemExit(start())
