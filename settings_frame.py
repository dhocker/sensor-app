#
# settings_frame.py - app settings
# Copyright © 2022 Dave Hocker (email: AtHomeX10@gmail.com)
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
from tkinter import Tk, Button, Label, Entry, Frame, LabelFrame, Checkbutton, IntVar, StringVar
from tkinter import font
from tkinter.ttk import Combobox
from configuration import Configuration
import logging


class LabeledCheckboxWidget:
    """
    A compound label + checkbox widget
    """
    def __init__(self, parent, label="", value=None, row=0, column=0):
        """
        A checkbox with leading label
        :param parent:
        :param label:
        :param value: The string "true or "false"
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = IntVar()
        self._var.set(value == "true")
        self._control = Checkbutton(parent, text="", variable=self._var, width=6, bd=2)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the check value as the string true or false
        :return:
        """
        v = self._var.get()
        if v:
            return "true"
        return "false"

    def focus(self):
        """
        Set the focus on this control. Used to handle input errors.
        :return:
        """
        self._control.focus()


class LabeledStringWidget:
    """
    A compound label + string entry widget
    """
    def __init__(self, parent, label="", value="", row=0, column=0):
        """
        An integer input widget with leading label
        :param parent:
        :param label:
        :param value: A string value
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = StringVar()
        self._var.set(value)
        self._control = Entry(parent, textvariable=self._var, width=len(value)+1, bd=2)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the integer value as the string true or false
        :return:
        """
        v = self._var.get()
        return v

    def focus(self):
        """
        Set the focus on this widget. Used for error handling.
        :return:
        """
        self._control.focus()


class LabeledIntWidget:
    """
    A compound label + numeric entry widget
    """
    def __init__(self, parent, label="", value=0, row=0, column=0):
        """
        An integer input widget with leading label
        :param parent:
        :param label:
        :param value: An integer value
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = IntVar()
        self._var.set(int(value))
        self._control = Entry(parent, textvariable=self._var, width=5, bd=2)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the integer value as the string true or false
        :return:
        """
        v = self._var.get()
        try:
            v = int(v)
        except ValueError as ex:
            raise ex
        return v

    def focus(self):
        """
        Set the focus on this widget. Used for error handling.
        :return:
        """
        self._control.focus()


class LabeledFloatWidget:
    """
    A compound label + numeric entry widget
    """
    def __init__(self, parent, label="", value=0.0, row=0, column=0):
        """

        :param parent:
        :param label:
        :param value: A decimal/float value
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = StringVar()
        self._var.set(str(value))
        self._control = Entry(parent, textvariable=self._var, width=5, bd=2)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the integer value as the string true or false
        :return:
        """
        v = self._var.get()
        try:
            v = float(v)
        except ValueError as ex:
            raise ex
        return v

    def focus(self):
        """
        Set the focus on this widget. Used for error handling.
        :return:
        """
        self._control.focus()


class LabeledComboboxWidget:
    """
    A compound label + combobox widget
    """
    def __init__(self, parent, label="", value="", value_list=[], row=0, column=0, width=6):
        """

        :param parent:
        :param label:
        :param values:
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = StringVar()
        self._var.set(value)
        self._control = Combobox(parent, textvariable=self._var, values=value_list, width=width)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the check value as the string true or false
        :return:
        """
        v = self._var.get()
        return v

    def focus(self):
        self._control.focus()


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
        self._mtn_entry_widgets = {}
        self._ste_entry_widgets = {}
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
        lh_frame = LabelFrame(self, text="Sensor Names", bd=2)
        lh_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")

        rh_frame = Frame(self)
        rh_frame.grid(row=0, column=1, padx=10, pady=5, sticky="n")

        ste_frame = LabelFrame(rh_frame, text="Settings", bd=2)
        ste_frame.grid(row=0, column=0, padx=10, pady=5, sticky="n")
        buttons_frame = Frame(rh_frame, bd=2)
        buttons_frame.grid(row=1, column=0, columnspan=2, sticky="ns")

        # mac to name list
        gr = 0
        for mac, kvn in self._config[Configuration.CFG_RUUVITAGS].items():
            lbl = Label(lh_frame, text=f"{mac}")
            lbl.grid(row=gr, column=0, padx=3, sticky="e")

            ent = Entry(lh_frame, width=10, bd=2)
            ent.insert(0, kvn["name"])
            ent.grid(row=gr, column=1, padx=3, pady=3)
            self._mtn_entry_widgets[mac] = ent

            gr += 1

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

        # Buttons
        cancel_button = Button(buttons_frame, text="Cancel", command=self.destroy)
        cancel_button.pack(side="left")
        save_button = Button(buttons_frame, text="Save", command=self._save_config)
        save_button.pack(side="right")

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

        Configuration.save_configuration()
        self._logger.info("Configuration file updated")

        # And, close the settings frame
        self._parent.update_frame()
        self.destroy()
