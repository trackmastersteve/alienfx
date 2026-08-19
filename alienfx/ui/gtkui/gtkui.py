#
# gtkui.py
#
# Copyright (C) 2013-2014 Ashwin Menon <ashwin.menon@gmail.com>
# Copyright (C) 2015-2024 Track Master Steve <trackmastersteve@gmail.com>
#
# Alienfx is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
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

""" GTK GUI interface to alienfx. 

This module provides the following classes:
AlienFXApp: The main GUI application.
"""

import argparse
import logging
import os
import shutil
import subprocess
import sys
import threading
import time
from importlib import resources

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import GLib

from alienfx.ui.gtkui.colour_palette import ColourPalette
from alienfx.core.prober import AlienFXProber
from alienfx.core.themefile import AlienFXThemeFile
from alienfx.ui.gtkui.action_renderer import AlienFXActionCellRenderer
from alienfx.ui.gtkui.action_renderer import AlienFXActions
        
class AlienFXApp(Gtk.Application):
    application_id = "io.github.trackmastersteve.alienfx"
    application_name = "AlienFX"
    wm_class = "alienfx"
    
    # These are the colours you can set a zone action to.
    colours = [
            "#000000",
            "#FFFFFF",
            "#00F3F1",
            "#00F89A",
            "#00FA52",
            "#00FF00",
            "#79F900",
            "#C1F800",
            "#F0E500",
            "#F0E500",
            "#FF4500",
            "#FF0000",
            "#FF006F",
            "#FF00B1",
            "#FF00F5",
            "#A400F5",
            "#6500F6",
            "#0000FF",
            "#004BF5",
            "#009AF4"
        ]
        
    def __init__(self, root_mode=False):
        GLib.set_prgname(self.wm_class)
        GLib.set_application_name(self.application_name)
        Gtk.Window.set_default_icon_name(self.wm_class)
        Gtk.Application.__init__(self, application_id=self.application_id)
        self.connect("activate", self.on_activate)
        self.root_mode = root_mode or os.geteuid() == 0
        self.controller = AlienFXProber.get_controller()
        self.themefile = AlienFXThemeFile(self.controller)
        self.selected_action = None
        self.action_type = self.themefile.KW_ACTION_TYPE_FIXED
        self.theme_edited = False
        self.set_theme_done = True
        self.apply_error = None
        self.apply_started_at = None
        self.apply_timeout_seconds = 30
        self.mode_context_id = None
        self.pkexec_path = shutil.which("pkexec")

    def _project_root(self):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))

    def _root_launcher_base_command(self):
        return [sys.executable, "-m", "alienfx.ui.gtkui.gtkui"]

    def _root_launcher_env_assignments(self):
        env_keys = [
            "DISPLAY",
            "XAUTHORITY",
            "XDG_RUNTIME_DIR",
            "DBUS_SESSION_BUS_ADDRESS",
            "WAYLAND_DISPLAY",
            "XDG_CURRENT_DESKTOP",
            "DESKTOP_SESSION",
            "LANG",
            "LC_ALL",
            "PATH",
        ]
        assignments = []
        for key in env_keys:
            value = os.environ.get(key)
            if value:
                assignments.append("{}={}".format(key, value))

        python_path = os.environ.get("PYTHONPATH", "")
        project_root = self._project_root()
        if project_root not in python_path.split(os.pathsep):
            python_path = os.pathsep.join([part for part in [python_path, project_root] if part])
        if python_path:
            assignments.append("PYTHONPATH={}".format(python_path))
        return assignments

    def _set_mode_status(self, message):
        statusbar = self.builder.get_object("statusbar")
        if self.mode_context_id is None:
            self.mode_context_id = statusbar.get_context_id("Mode")
        statusbar.pop(self.mode_context_id)
        statusbar.push(self.mode_context_id, message)

    def _refresh_privilege_ui(self):
        auth_button = self.builder.get_object("toolbutton_authenticate")
        if self.root_mode:
            auth_button.set_sensitive(False)
            auth_button.set_tooltip_text("AlienFX is already running with root privileges.")
            self._set_mode_status("Running in root mode.")
            return

        if self.pkexec_path is None:
            auth_button.set_sensitive(False)
            auth_button.set_tooltip_text("Install pkexec to relaunch AlienFX with root privileges.")
            self._set_mode_status("Running in user mode. Root mode requires pkexec.")
            return

        auth_button.set_sensitive(True)
        auth_button.set_tooltip_text("Authenticate and relaunch AlienFX in root mode.")
        self._set_mode_status("Running in user mode. Use Authenticate for root mode.")

    def _show_root_mode_error(self, message):
        self.builder.get_object("toolbar").set_sensitive(True)
        self._refresh_privilege_ui()
        main_window = self.builder.get_object("main_window")
        dialog = Gtk.MessageDialog(
            main_window,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.CLOSE,
            message,
        )
        dialog.run()
        dialog.destroy()

    def _launch_root_mode_worker(self):
        command = [
            self.pkexec_path,
            "env",
            *self._root_launcher_env_assignments(),
            *self._root_launcher_base_command(),
            "--spawn-root-ui",
        ]
        try:
            completed = subprocess.run(
                command,
                cwd=self._project_root(),
                check=False,
            )
        except Exception as exc:
            GLib.idle_add(
                self._show_root_mode_error,
                "Failed to start root mode: {}".format(exc),
            )
            return

        if completed.returncode == 0:
            GLib.idle_add(self.quit)
            return

        GLib.idle_add(
            self._show_root_mode_error,
            "Authentication was cancelled or root mode failed to start.",
        )

    def on_action_authenticate_activate(self, widget):
        if self.root_mode:
            return
        if self.pkexec_path is None:
            self._show_root_mode_error(
                "Unable to authenticate because pkexec is not installed on this system."
            )
            return

        self.builder.get_object("toolbar").set_sensitive(False)
        self._set_mode_status("Waiting for authentication to enter root mode...")
        threading.Thread(target=self._launch_root_mode_worker, daemon=True).start()

    def enable_delete_theme_button(self, enable):
        """ Enable or disable the "Delete Theme" button."""
        self.builder.get_object("toolbutton_delete_theme").set_sensitive(enable)
        
    def ask_discard_changes(self):
        """ Ask the user if he wants to discard theme edits."""
        main_window = self.builder.get_object("main_window")
        dialog = Gtk.MessageDialog(main_window, 
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO,
            "The current theme has unsaved changes. Do you want to discard them?")
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES

    def _resource_path(self, *parts):
        resource = resources.files("alienfx.ui.gtkui")
        for part in parts:
            resource = resource.joinpath(part)
        return resource
            
    def on_action_new_theme_activate(self, widget):
        """ Handler for when the "New Theme" action is triggered."""
        if self.theme_edited:
            if not self.ask_discard_changes():
                return
                
        self.themefile = AlienFXThemeFile(self.controller)
        self.themefile.set_default_theme()
        self.load_theme("New Theme")
        self.set_theme_dirty(False)
        self.theme_loaded_from_file = False
        self.enable_delete_theme_button(False)
        
    def on_action_open_theme_activate(self, widget):
        """ Handler for when the "Open Theme" action is triggered."""
        if self.theme_edited:
            if not self.ask_discard_changes():
                return
                
        themes = self.themefile.get_themes()
        open_theme_list_store = self.builder.get_object("open_theme_list_store")
        open_theme_list_store.clear()
        for theme in themes:
            open_theme_list_store.append([theme])
        self.builder.get_object("open_theme_dialog").show()
        
    def on_action_save_theme_activate(self, widget):
        """ Handler for when the "Save Theme" action is triggered."""
        if self.themefile.theme_name == "":
            self.on_action_save_theme_as_activate(widget)
        else:
            self.themefile.save(self.themefile.theme_name)
            self.set_theme_dirty(False)
            self.theme_loaded_from_file = True
            self.enable_delete_theme_button(True)
        
    def on_action_save_theme_as_activate(self, widget):
        """ Handler for when the "Save Theme As" action is triggered."""
        themes = self.themefile.get_themes()
        saveas_theme_list_store = self.builder.get_object("saveas_theme_list_store")
        saveas_theme_list_store.clear()
        for theme in themes:
            saveas_theme_list_store.append([theme])
        self.builder.get_object("saveas_theme_name").set_text("")
        self.builder.get_object("saveas_theme_dialog").show()
    
    def on_action_delete_theme_activate(self, widget):
        """ Handler for when the "Delete Theme" action is triggered."""
        main_window = self.builder.get_object("main_window")
        dialog = Gtk.MessageDialog(main_window, 
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.YES_NO,
            ("Are you sure you want to delete this theme from disk? " +  
            "This cannot be undone!"""))
        response = dialog.run()
        dialog.destroy()
        if response == Gtk.ResponseType.NO:
            return
        if self.themefile.delete_theme_from_disk():
            self.theme_loaded_from_file = False
            self.enable_delete_theme_button(False)
            self.load_theme("New Theme")
            
    def on_action_delete_activate(self, widget):
        """ Handler for when the "Delete Action" action is triggered."""
        if self.selected_action is None:
            return
            
        (treeiter, action_index) = self.selected_action
        model = self.zone_list_view.get_model()
        actions = model[treeiter][1]
        del actions.actions[action_index:action_index+1]
        if len(actions.actions) == 1:
            self.builder.get_object("toolbutton_delete").set_sensitive(False)
        model[treeiter][1] = actions
        action_index -= 1
        if action_index < 0:
            action_index = 0
        self.action_cell_renderer.select_action_at_index(action_index)
        self.selected_action = (treeiter, action_index)
        self.set_theme_dirty(True)
        
    def on_action_add_activate(self, widget):
        """ Handler for when the "Add Action" action is triggered."""
        if self.selected_action is None:
            return
            
        (treeiter, action_index) = self.selected_action
        model = self.zone_list_view.get_model()
        actions = model[treeiter][1]
        new_action = self.themefile.make_zone_action(self.action_type, [[15, 15, 15]])
        insert_index = action_index + 1 if action_index is not None else len(actions.actions)
        actions.actions.insert(insert_index, new_action)
        self.builder.get_object("toolbutton_delete").set_sensitive(True)
        model[treeiter][1] = actions
        self.set_theme_dirty(True)
        
    def set_theme_dirty(self, dirty):
        """ Set the current theme dirty, i.e. the current theme has 
        unsaved edits.
        """
        self.theme_edited = dirty
        title = self.builder.get_object("main_window").get_title()
        if dirty:
            if title[0] != "*":
                title = "*" + title
        else:
            if title[0] == "*":
                title = title[1:]
        self.builder.get_object("main_window").set_title(title)
        
    def set_theme(self):
        """ Set the current theme on the computer."""
        try:
            if self.controller is None:
                raise RuntimeError("No AlienFX controller available")
            self.controller.set_theme(self.themefile)
            self.themefile.applied()
            self.apply_error = None
        except Exception as exc:
            self.apply_error = str(exc)
            logging.exception("Error applying theme")
        self.set_theme_done = True
        
    def set_theme_done_cb(self):
        """ This idle task updates the GUI when the theme has been sent to the
        AlienFX controller."""
        # Prevent UI from remaining frozen forever if controller apply blocks.
        if (not self.set_theme_done and
                self.apply_started_at is not None and
                (time.monotonic() - self.apply_started_at) > self.apply_timeout_seconds):
            self.apply_error = (
                "The controller may be unresponsive and is timed out after {}s.".format(
                    self.apply_timeout_seconds
                )
            )
            self.set_theme_done = True

        if self.set_theme_done:
            spinner = self.builder.get_object("spinner")
            spinner.stop()
            spinner.hide()
            statusbar = self.builder.get_object("statusbar")
            statusbar.pop(self.context_id)
            self.builder.get_object("toolbar").set_sensitive(True)
            if self.apply_error is not None:
                # Keep error visible in statusbar as requested.
                statusbar.push(self.context_id, "Apply failed: {}".format(self.apply_error))
                main_window = self.builder.get_object("main_window")
                dialog = Gtk.MessageDialog(
                    main_window,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.CLOSE,
                    "Failed: {}".format(self.apply_error),
                )
                dialog.run()
                dialog.destroy()
                self.apply_error = None
            else:
                statusbar.push(self.context_id, "Theme applied.")
            self.apply_started_at = None
            return False
        else:
            return True
        
    def on_action_apply_activate(self, widget):
        """ Handler for when the "Apply Theme" action is triggered."""
        self.builder.get_object("toolbar").set_sensitive(False)
        statusbar = self.builder.get_object("statusbar")
        self.context_id = statusbar.get_context_id("Apply")
        statusbar.push(self.context_id, "Applying theme...")
        spinner = self.builder.get_object("spinner")
        spinner.show()
        spinner.start()
        self.set_theme_done = False
        self.apply_started_at = time.monotonic()
        self.apply_timeout_seconds = 10
        GLib.idle_add(self.set_theme_done_cb)
        self.set_theme_thread = threading.Thread(target=self.set_theme, daemon=True)
        self.set_theme_thread.start()

    def set_window_title(self, theme_name):
        """ Set the window title from the current theme name."""
        self.builder.get_object("main_window").set_title(theme_name + " - Alien FX")
        
    def load_theme(self, theme_name=None):
        """ Load a theme and display it in the GUI. If a theme name is supplied
        then show it in the window title; otherwise get the theme name from the
        theme file currently loaded."""
        normal_zone_list_store = self.builder.get_object("normal_zone_list_store")
        power_zone_list_store = self.builder.get_object("power_zone_list_store")
        normal_zones_added = set()
        normal_zone_list_store.clear()
        power_zone_list_store.clear()
        # If controller isn't available, nothing to load
        if not self.controller:
            return
        zones = self.controller.zone_map
        for zone in zones:
            if zone in self.controller.power_zones:
                # Get available power states from controller's state_map
                # This handles both laptop (with battery states) and desktop (AC-only) controllers
                power_states = []
                
                # Add AC states if available
                ac_states = [
                    self.controller.STATE_AC_SLEEP,
                    self.controller.STATE_AC_CHARGED,
                    self.controller.STATE_AC_CHARGING,
                ]
                for state in ac_states:
                    if state in self.controller.state_map:
                        power_states.append(state)
                
                # Add battery states if available (laptop controllers)
                battery_states = [
                    self.controller.STATE_BATTERY_SLEEP,
                    self.controller.STATE_BATTERY_ON,
                    self.controller.STATE_BATTERY_CRITICAL,
                ]
                for state in battery_states:
                    if state in self.controller.state_map:
                        power_states.append(state)
                
                for state in power_states:
                    a = AlienFXActions()
                    a.actions = self.themefile.get_zone_actions(state, zone)
                    power_zone_list_store.append([state, a])

        # Keep compatibility with themes/controllers that use a dedicated
        # power zone for the power button, even if the controller doesn't have a separate power button zone.
        normal_states = []

        zone_states = [
            self.controller.ZONE_LEFT_KEYBOARD,
            self.controller.ZONE_MIDDLE_LEFT_KEYBOARD,
            self.controller.ZONE_MIDDLE_RIGHT_KEYBOARD,
            self.controller.ZONE_RIGHT_KEYBOARD,
            self.controller.ZONE_RIGHT_SPEAKER,
            self.controller.ZONE_LEFT_SPEAKER,
            self.controller.ZONE_ALIEN_HEAD,
            self.controller.ZONE_LEFT_SIDE,
            self.controller.ZONE_LOGO,
            self.controller.ZONE_TOUCH_PAD,
            self.controller.ZONE_MEDIA_BAR,
            self.controller.ZONE_STATUS_LEDS,
            self.controller.ZONE_POWER_BUTTON,
            self.controller.ZONE_HDD_LEDS,
            self.controller.ZONE_RIGHT_DISPLAY,  # LED-bar display right side, as built in the AW17R4
            self.controller.ZONE_LEFT_DISPLAY,  # LED-bar display left side, as built in the AW17R4         
        ]                
        for state in zone_states:
            if state in self.controller.power_zones:
                normal_states.append(state)                
        
        for state in normal_states:
            a = AlienFXActions()
            a.actions = self.themefile.get_zone_actions(self.controller.STATE_BOOT, state)
            normal_zone_list_store.append([state, a])
            normal_zones_added.add(state)

        self.zone_list_view.set_model(normal_zone_list_store)
        self.builder.get_object("radiobutton_normal_zones").set_active(True)
        if theme_name is not None:
            self.set_window_title(theme_name)
        elif self.themefile.theme_name == "":
            self.set_window_title("New theme")
        else:
            self.set_window_title(self.themefile.theme_name)
        self.enable_action_edit_controls(False)
    
    # Dialog box close handlers
    def on_dialog_close(self, dialog):
        # Instead of closing a dialog box, just hide it.
        GObject.signal_stop_emission_by_name(dialog, "close")
        dialog.hide()
        
    # Open dialog box handlers        
    def on_open_theme_cancel_clicked(self, button):
        self.builder.get_object("open_theme_dialog").hide()
        
    def do_load_theme(self, theme_name):
        self.themefile.load(theme_name)
        self.load_theme()
        self.builder.get_object("open_theme_dialog").hide()
        self.set_theme_dirty(False)
        self.theme_loaded_from_file = True
        self.enable_delete_theme_button(True)
        
    def on_open_theme_list_view_row_activated(self, treeview, path, column):
        """ Handler for when a theme in the theme list is double-clicked."""
        model = treeview.get_model()
        treeiter = model.get_iter(path)
        self.do_load_theme(model[treeiter][0])
        
    def on_open_theme_ok_clicked(self, button):
        """ Handler for when the OK button is clicked in the Open Theme dialog."""
        model, treeiter = self.open_theme_list_view.get_selection().get_selected()
        if treeiter is not None:
            self.do_load_theme(model[treeiter][0])
        
    def on_open_theme_list_selection_changed(self, selection):
        """ Handler for when a theme name is selected in the Open Theme dialog."""
        self.builder.get_object("open_theme_ok").set_sensitive(selection.count_selected_rows() > 0)
        
    # Save-as dialog box handlers
    def do_saveas_theme(self, theme_name):
        self.themefile.save(theme_name)
        self.set_window_title(self.themefile.theme_name)
        self.builder.get_object("saveas_theme_dialog").hide()
        self.set_theme_dirty(False)
        self.theme_loaded_from_file = True
        self.enable_delete_theme_button(True)
        
    def on_saveas_theme_name_activate(self, entry):
        """ Handler for when <Enter> is pressed in the theme name entry box."""
        self.do_saveas_theme(entry.get_text())
        
    def on_saveas_theme_list_view_row_activated(self, treeview, path, column):
        """ Handler for when a theme in the theme list is double-clicked."""
        model = treeview.get_model()
        treeiter = model.get_iter(path)
        self.do_saveas_theme(model[treeiter][0])
        
    def on_saveas_theme_ok_clicked(self, button):
        """ Handler for when the OK button is clicked in the Save Theme As dialog."""
        name = self.builder.get_object("saveas_theme_name").get_text()
        self.do_saveas_theme(name)
        
    def on_saveas_theme_cancel_clicked(self, button):
        self.builder.get_object("saveas_theme_dialog").hide()
        
    def on_saveas_theme_list_selection_changed(self, selection):
        """ Handler for when a theme name is selected in the Save Theme As dialog."""
        model, treeiter = selection.get_selected()
        if treeiter is not None:
            name = model[treeiter][0]
            self.builder.get_object("saveas_theme_name").set_text(name)
        
    def on_saveas_theme_name_changed(self, editable):
        self.builder.get_object("saveas_theme_ok").set_sensitive(
            len(editable.get_text().strip()) > 0)
        
    # Zone select button handlers
    def on_radiobutton_normal_zones_toggled(self, button):
        if button.get_active():
            self.zone_list_view.set_model(self.builder.get_object("normal_zone_list_store"))
            self.enable_action_edit_controls(False)
        
    def on_radiobutton_power_zone_toggled(self, button):
        if button.get_active():
            self.zone_list_view.set_model(self.builder.get_object("power_zone_list_store"))
            self.enable_action_edit_controls(False)
        
    def on_activate(self, data=None):
        self.builder = Gtk.Builder()
        with resources.as_file(self._resource_path("glade", "ui.glade")) as ui_glade:
            self.builder.add_from_file(str(ui_glade))
        
        self.zone_list_view = self.builder.get_object("zone_list_view")
        self.zone_list_view.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.zone_list_view.connect(
            "button-press-event", self.zone_item_selected)
        self.action_cell_renderer = AlienFXActionCellRenderer(
            treeview=self.zone_list_view, max_colour_val=0xf)
        col_colour = Gtk.TreeViewColumn(
            "Actions", self.action_cell_renderer, actions=1)
        self.zone_list_view.append_column(col_colour)
        
        self.open_theme_list_view = self.builder.get_object("open_theme_list_view")
        self.open_theme_list_view.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.open_theme_list_view.get_selection().connect(
            "changed", self.on_open_theme_list_selection_changed)
            
        self.saveas_theme_list_view = self.builder.get_object("saveas_theme_list_view")
        self.saveas_theme_list_view.get_selection().set_mode(Gtk.SelectionMode.SINGLE)
        self.saveas_theme_list_view.get_selection().connect(
            "changed", self.on_saveas_theme_list_selection_changed)
            
        self.properties_frame = self.builder.get_object("properties_frame")
        
        self.palette1 = ColourPalette(
            self.colours, max_colour_val=0xf, num_rows=2, num_cols=10, 
            horizontal=True, selected_handler=self.on_colour_selected)
        self.builder.get_object("colour_palette1").add(self.palette1)
        
        self.palette2 = ColourPalette(
            self.colours, max_colour_val=0xf, num_rows=2, num_cols=10, 
            horizontal=True, selected_handler=self.on_colour_selected)
        self.builder.get_object("colour_palette2").add(self.palette2)
        self.palette2.set_sensitive(False)
        
        self.builder.connect_signals(self)
        main_window = self.builder.get_object("main_window")
        with resources.as_file(resources.files("alienfx").joinpath(
            "data", "icons", "hicolor", "scalable", "apps", "alienfx.svg"
        )) as icon_file:
            main_window.set_icon_from_file(str(icon_file))
        main_window.set_icon_name(self.wm_class)
        main_window.set_wmclass(self.wm_class, self.application_name)
        main_window.show_all()
        self.add_window(main_window)
        self._refresh_privilege_ui()
        
        if self.controller is None:
            Gtk.MessageDialog(
                main_window, Gtk.DialogFlags.MODAL, 
                Gtk.MessageType.ERROR, 
                Gtk.ButtonsType.CLOSE, 
                "No supported Alien FX controller found!").run()
            quit()
            
        self.themefile = AlienFXThemeFile(self.controller)
        last_theme_loaded = self.themefile.load_last_theme()
        if last_theme_loaded:
            self.load_theme("Current Theme")
        else:
            self.load_theme("New Theme")
        self.theme_loaded_from_file = False
        self.enable_delete_theme_button(False)
        
    def on_main_window_delete_event(self, widget, event):
        if self.theme_edited:
            if self.ask_discard_changes():
                widget.destroy()
        else:
            widget.destroy()
        return True
        
    # Action edit control handlers
    def on_radiobutton_fixed_colour_toggled(self, button):
        if button.get_active():
            self.palette2.set_sensitive(False)
            self.action_type = self.themefile.KW_ACTION_TYPE_FIXED
    
    def on_radiobutton_blinking_colour_toggled(self, button):
        if button.get_active():
            self.palette2.set_sensitive(False)
            self.action_type = self.themefile.KW_ACTION_TYPE_BLINK
                    
    def on_radiobutton_morphing_colour_toggled(self, button):
        if button.get_active():
            self.palette2.set_sensitive(True)
            self.action_type = self.themefile.KW_ACTION_TYPE_MORPH
        
    def on_colour_selected(self, sender=None, data=None):
        if self.selected_action is None:
            return
        if sender is None:
            return
            
        colour = sender.get_colour()
        (treeiter, action_index) = self.selected_action
        model = self.zone_list_view.get_model()
        actions = model[treeiter][1]
        action = actions.actions[action_index]
        self.themefile.set_action_type(action, self.action_type)
        old_colours = self.themefile.get_action_colours(action)
        if (self.action_type in [
                self.themefile.KW_ACTION_TYPE_FIXED, 
                self.themefile.KW_ACTION_TYPE_BLINK]):
            if len(old_colours) == 0:
                old_colours = [[0, 0, 0]]
            elif len(old_colours) > 1:
                old_colours = old_colours[0:1]
        if self.action_type == self.themefile.KW_ACTION_TYPE_MORPH:
            if len(old_colours) == 0:
                old_colours = [[0, 0, 0], [0, 0, 0]]
            elif len(old_colours) == 1:
                old_colours.append([0, 0, 0])
            elif len(old_colours) > 2:
                old_colours = old_colours[0:2]
        parent = sender.get_parent() if sender is not None else None
        if parent == self.palette1:
            old_colours[0] = colour
        if parent == self.palette2:
            old_colours[1] = colour
        self.themefile.set_action_colours(action, old_colours)
        model[treeiter][1] = actions
        self.set_theme_dirty(True)
                    
    def enable_action_edit_controls(self, enable):
        self.builder.get_object("toolbutton_add").set_sensitive(enable)
        self.builder.get_object("toolbutton_delete").set_sensitive(enable)
        self.properties_frame.set_sensitive(enable)
        
    def zone_item_selected(self, treeview, event):
        (path, column, cell_x, cell_y) = treeview.get_path_at_pos(event.x, event.y)
        self.selected_action = None
        self.enable_action_edit_controls(False)
        self.action_cell_renderer.select_action_at_x(None)
        
        if column.get_title() == "Actions":
            action_index = self.action_cell_renderer.select_action_at_x(cell_x)
            model = treeview.get_model()
            treeiter = model.get_iter(path)
            actions = model[treeiter][1]
            if action_index is not None and action_index < len(actions.actions):
                self.enable_action_edit_controls(True)
                self.selected_action = (treeiter, action_index)
                if len(actions.actions) == 1:
                    self.builder.get_object("toolbutton_delete").set_sensitive(False)
        
def start():
    """ Entry point for the GTK GUI interface to alienfx. """
    args = parse_args()
    if args.spawn_root_ui:
        return spawn_root_ui()
    app = AlienFXApp(root_mode=args.root_mode)
    app.run(None)
    return 0


def parse_args(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--root-mode", action="store_true")
    parser.add_argument("--spawn-root-ui", action="store_true")
    return parser.parse_args(argv)


def spawn_root_ui():
    env = os.environ.copy()
    command = [
        sys.executable,
        "-m",
        "alienfx.ui.gtkui.gtkui",
        "--root-mode",
    ]
    try:
        subprocess.Popen(
            command,
            cwd=os.getcwd(),
            env=env,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(start())
