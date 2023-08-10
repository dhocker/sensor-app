#
# settings_frame.py - app settings
# Copyright © 2023 Dave Hocker (email: AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE file).  If not, see <http://www.gnu.org/licenses/>.
#


import datetime
from tkinter import Tk, Button, Label, Entry, Frame, LabelFrame, Checkbutton, IntVar, StringVar, Listbox, Scrollbar
from tkinter import LEFT, RIGHT, BOTTOM, END, BOTH, VERTICAL, DISABLED, NORMAL
from tkinter import font
from tkinter.simpledialog import askstring
from custom_widgets import *
from configuration import Configuration
import logging


class SettingsFrame(Frame):
    """
    The settings page as a full window overlay
    """
    def __init__(self, parent, width=800, height=480):
        """
        Settings page editor
        :param parent: Typically the main window frame
        :param width: Width for the settings frame
        :param height: Height of the settings frame
        """
        super().__init__(parent, width=width, height=height)
        self._parent = parent

        # Create a logger
        self._logger = logging.getLogger("sensor_app")

        # Get the configuration
        self._config = Configuration.get_configuration()

        # Window metrics
        sw = width
        sh = height
        self._logger.info(f"Window size: {sw}x{sh}")

        self.background_color = "#ffffff"
        self.highlight_color = "#e0e0e0"

        # Create window widgets
        self._mtn_lb_macs = []
        self._mtn_entry_widgets = {}
        self._ste_entry_widgets = {}
        self._mtn_edit_button = None
        self._mtn_remove_button = None
        self._selected_index = -1
        self._mtn_listbox = None
        self._create_widgets(sw, sh)

    def _create_widgets(self, sw, sh):
        """
        Create all the widgets on the settings page
        :param sw:
        :param sh:
        :return:
        """
        # Two frames (lh and rh)
        # - mac to name table
        # - all other settings
        lh_frame = LabelFrame(self, text="Sensor Names", bd=5)
        lh_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")

        rh_frame = Frame(self)
        rh_frame.grid(row=0, column=1, padx=10, pady=5, ipadx=10, ipady=10, sticky="n")

        ste_frame = LabelFrame(rh_frame, text="Settings", bd=2)
        ste_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")

        # mac-to-name listbox
        self._mtn_listbox = Listbox(lh_frame, height=10, width=25)
        self._mtn_listbox.pack(side=LEFT, fill=BOTH, padx=5, pady=2)
        mtn_scrollbar = Scrollbar(lh_frame, orient=VERTICAL)
        mtn_scrollbar.pack(side=RIGHT, fill=BOTH)

        # mac to name list
        self._mtn_lb_macs = []
        for mac, kvn in self._config[Configuration.CFG_RUUVITAGS].items():
            self._mtn_lb_macs.append(mac)
        self._load_mtn_listbox()

        # Hook up scrollbar and listbox
        self._mtn_listbox.config(yscrollcommand=mtn_scrollbar.set)
        mtn_scrollbar.config(command=self._mtn_listbox.yview)
        # Handle item selected event
        self._mtn_listbox.bind('<<ListboxSelect>>', self._mtn_selected)

        # Create disabled buttons for removing/editingl listbox items
        # The buttons are enabled wnen a listbox item is selected
        # TODO Implement remove mtn item
        mtn_button_frame = Frame(self)
        self._mtn_edit_button = Button(mtn_button_frame, text="Edit", command=self._edit_mtn_name, state=DISABLED)
        self._mtn_edit_button.grid(row=0, column=0)
        self._mtn_remove_button = Button(mtn_button_frame, text="Remove", command=self._remove_mtn_name, state=DISABLED)
        self._mtn_remove_button.grid(row=0, column=1)
        mtn_add_button = Button(mtn_button_frame, text="Add", command=self._add_mtn_name)
        mtn_add_button.grid(row=0, column=2)
        mtn_button_frame.grid(row=1, column=0)

        # Other named settings in a brute force implementation
        # Use test data
        gr = 0
        value = self._config["use_test_data"].lower()
        widget = LabeledCheckboxWidget(ste_frame, label="use_test_data", value=value, row=gr, column=0)
        self._ste_entry_widgets["use_test_data"] = widget
        gr += 1

        value = self._config["debug_sensors"].lower()
        widget = LabeledCheckboxWidget(ste_frame, label="debug_sensors", value=value, row=gr, column=0)
        self._ste_entry_widgets["debug_sensors"] = widget
        gr += 1

        value = self._config["log_console"].lower()
        widget = LabeledCheckboxWidget(ste_frame, label="log_console", value=value, row=gr, column=0)
        self._ste_entry_widgets["log_console"] = widget
        gr += 1

        value_list = ["debug", "info", "warn", "error"]
        value = self._config["log_level"].lower()
        widget = LabeledComboboxWidget(ste_frame, label="log_level",
                                       value=value, value_list=value_list,
                                       row=gr, column=0)
        self._ste_entry_widgets["log_level"] = widget
        gr += 1

        value_list = ["F", "C"]
        value = self._config["temperature_format"].upper()
        widget = LabeledComboboxWidget(ste_frame, label="temperature_format",
                                       value=value, value_list=value_list,
                                       row=gr, column=0, width=2)
        self._ste_entry_widgets["temperature_format"] = widget
        gr += 1

        value = self._config["sensors_per_row"]
        widget = LabeledIntWidget(ste_frame, label="sensors_per_row",
                                       value=value,
                                       row=gr, column=0)
        self._ste_entry_widgets["sensors_per_row"] = widget
        gr += 1

        value = self._config["update_interval"]
        widget = LabeledFloatWidget(ste_frame, label="update_interval",
                                       value=value,
                                       row=gr, column=0)
        self._ste_entry_widgets["update_interval"] = widget
        gr += 1

        value = self._config["offline_time"]
        widget = LabeledIntWidget(ste_frame, label="offline_time",
                                       value=value,
                                       row=gr, column=0)
        self._ste_entry_widgets["offline_time"] = widget
        gr += 1

        # TODO Make a widget for color
        value = self._config["offline_color"]
        widget = LabeledStringWidget(ste_frame, label="offline_color",
                                       value=value,
                                       row=gr, column=0)
        self._ste_entry_widgets["offline_color"] = widget
        gr = 0

        value = self._config["low_battery_threshold"]
        widget = LabeledIntWidget(ste_frame, label="low_battery_threshold",
                                  value=value,
                                  row=gr, column=2)
        self._ste_entry_widgets["low_battery_threshold"] = widget
        gr += 1

        value = self._config["low_battery_color"]
        widget = LabeledStringWidget(ste_frame, label="low_battery_color",
                                     value=value,
                                     row=gr, column=2)
        self._ste_entry_widgets["low_battery_color"] = widget
        gr += 1

        value = self._config["normal_background_color"]
        widget = LabeledStringWidget(ste_frame, label="normal_background_color",
                                     value=value,
                                     row=gr, column=2)
        self._ste_entry_widgets["normal_background_color"] = widget
        gr += 1

        value = self._config[Configuration.CFG_OVERVIEW_FONT_SIZE]
        widget = LabeledIntWidget(ste_frame, label=Configuration.CFG_OVERVIEW_FONT_SIZE,
                                     value=value,
                                     row=gr, column=2)
        self._ste_entry_widgets[Configuration.CFG_OVERVIEW_FONT_SIZE] = widget
        gr += 1

        # Cancel/save buttons
        buttons_frame = Frame(self)
        buttons_frame.grid(row=1, column=1, columnspan=2, sticky="ns")
        cancel_button = Button(buttons_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left")
        save_button = Button(buttons_frame, text="Save All Settings", command=self._save_config)
        save_button.pack(side="right")

    def _edit_mtn_name(self):
        """
        Edit the currently selected mac-to-name listbox entry. Depends on being
        called only after an item is selected.
        :return:
        """
        mac = self._mtn_lb_macs[self._selected_index]
        name = self._config[Configuration.CFG_RUUVITAGS][mac]["name"]
        name = askstring("Edit name of sensor", mac, initialvalue=name, parent=self)

        # If the dialog was canceled, the name is None
        if name is None:
            return

        # Update the config
        self._config[Configuration.CFG_RUUVITAGS][mac]["name"] = name

        # Update the mtn listbox
        # Clear the listbox and reload
        self._load_mtn_listbox()

    def _remove_mtn_name(self):
        """
        Remove the currently selected mac-to-name entry
        :return:
        """
        pass

    def _add_mtn_name(self):
        """
        Add a new mac-to-name entry
        :return:
        """
        pass

    def _load_mtn_listbox(self):
        """
        Load/reload the mac-to-name listbox
        :return:
        """
        self._mtn_listbox.delete(0, len(self._mtn_lb_macs))
        for mac, kvn in self._config[Configuration.CFG_RUUVITAGS].items():
            item = f"{mac}:\t{kvn['name']}"
            self._mtn_listbox.insert(END, item)

    def _mtn_selected(self, event):
        """
        A mac-to-name listbox entry has been selected
        :param event: object defining event. event.widget is the listbox object.
        :return:
        """
        # Note here that Tkinter passes an event object to onselect()
        w = event.widget
        selected_index = w.curselection()

        # Nothing selected
        if len(selected_index) == 0:
            self._mtn_edit_button.config(state=DISABLED)
            self._mtn_remove_button.config(state=DISABLED)
            return

        self._selected_index = selected_index[0]
        mac = self._mtn_lb_macs[self._selected_index]
        name = self._config[Configuration.CFG_RUUVITAGS][mac]["name"]
        # print('You selected item %d: "%s"' % (index, mac))
        print(f"You selected item: {self._selected_index} mac: {mac} name: {name}")
        self._mtn_edit_button.config(state=NORMAL)
        self._mtn_remove_button.config(state=NORMAL)

    def _save_config(self):
        """
        Save all the settings back into the configuration file
        :return:
        """
        # Retrieve names from sensor names list
        for mac, name_entry in self._mtn_entry_widgets.items():
            name = name_entry.get()
            self._config[Configuration.CFG_RUUVITAGS][mac]["name"] = name

        # Retrieve settings
        use_test_data = self._ste_entry_widgets["use_test_data"].get()
        self._config["use_test_data"] = use_test_data
        debug_sensors = self._ste_entry_widgets["debug_sensors"].get()
        self._config["debug_sensors"] = debug_sensors
        log_console = self._ste_entry_widgets["log_console"].get()
        self._config["log_console"] = log_console
        log_level = self._ste_entry_widgets["log_level"].get()
        self._config["log_level"] = log_level
        temperature_format = self._ste_entry_widgets["temperature_format"].get()
        self._config["temperature_format"] = temperature_format
        temperature_format = self._ste_entry_widgets["temperature_format"].get()
        self._config["temperature_format"] = temperature_format

        try:
            sensors_per_row = self._ste_entry_widgets["sensors_per_row"].get()
            self._config["sensors_per_row"] = sensors_per_row
        except:
            self._ste_entry_widgets["sensors_per_row"].focus()
            return

        try:
            update_interval = self._ste_entry_widgets["update_interval"].get()
            self._config["update_interval"] = update_interval
        except:
            self._ste_entry_widgets["update_interval"].focus()
            return

        try:
            offline_time = self._ste_entry_widgets["offline_time"].get()
            self._config["offline_time"] = offline_time
        except:
            self._ste_entry_widgets["offline_time"].focus()
            return

        try:
            offline_color = self._ste_entry_widgets["offline_color"].get()
            self._config["offline_color"] = offline_color
        except:
            self._ste_entry_widgets["offline_color"].focus()
            return

        try:
            low_battery_threshold = self._ste_entry_widgets["low_battery_threshold"].get()
            self._config["low_battery_threshold"] = low_battery_threshold
        except:
            self._ste_entry_widgets["low_battery_threshold"].focus()
            return

        try:
            low_battery_color = self._ste_entry_widgets["low_battery_color"].get()
            self._config["low_battery_color"] = low_battery_color
        except:
            self._ste_entry_widgets["low_battery_color"].focus()
            return

        try:
            normal_background_color = self._ste_entry_widgets["normal_background_color"].get()
            self._config["normal_background_color"] = normal_background_color
        except:
            self._ste_entry_widgets["normal_background_color"].focus()
            return

        try:
            overview_font_size = self._ste_entry_widgets[Configuration.CFG_OVERVIEW_FONT_SIZE].get()
            self._config[Configuration.CFG_OVERVIEW_FONT_SIZE] = overview_font_size
        except:
            self._ste_entry_widgets[Configuration.CFG_OVERVIEW_FONT_SIZE].focus()
            return

        Configuration.save_configuration()
        self._logger.info("Configuration file updated")

        # And, close the settings frame
        self._parent.update_frame()
        self.destroy()
