#
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
from datetime import datetime
import tkinter
from tkinter import Tk, Frame, Button, Label, LabelFrame, messagebox, Toplevel
from tkinter import Text, INSERT
from tkinter import Label
from tkinter import font
from sensor_details_dlg import SensorDetailsDlg
from configuration import Configuration


class SensorWidget(LabelFrame):
    """
    Displays the values for one sensor. Click anywhere on the frame to see sensor details.
    """
    # The values that will be displayed. The key and its label.
    _SENSOR_VALUE_KEYS = {
        "temperature": "temp",
        "humidity": "humid"
    }

    def __init__(self, parent, id, name, sensor_data):
        self._config = Configuration.get_configuration()
        self._lbl_font = font.Font(family="Arial", size=self._config[Configuration.CFG_OVERVIEW_FONT_SIZE])
        self._bd = 6
        self._bg = self._determine_background_color(sensor_data)

        super(SensorWidget, self).__init__(parent,
                                           text=f"{name}",
                                           font=self._lbl_font,
                                           bd=self._bd,
                                           bg=self._bg,
                                           relief=tkinter.RIDGE)

        # Handle a click in the frame
        self.bind("<Button-1>", self._show_details)

        gr = 0
        self._sensor_labels = {}
        self._sensor_value_labels = {}
        for data_value_key, data_value_name in SensorWidget._SENSOR_VALUE_KEYS.items():
            # Sensor value name and its value. Take a click on either label.
            label = Label(self, text=f"{data_value_name}", font=self._lbl_font, bg=self._bg)
            label.bind("<Button-1>", self._show_details)
            label.grid(row=gr, column=0, sticky="W", padx=1, pady=1)
            self._sensor_labels[data_value_key] = label

            label = Label(self, text=f"{sensor_data[data_value_key]:5.1f}", font=self._lbl_font, bg=self._bg)
            label.bind("<Button-1>", self._show_details)
            label.grid(row=gr, column=1, sticky="W", padx=1, pady=1)
            self._sensor_value_labels[data_value_key] = label

            gr += 1

        # A button for displaying all the details of a sensor's data
        # self._show_details_button = Button(self, text="Show Details", height=1, command=self._show_details)
        # self._show_details_button.grid(row=gr, column=0, columnspan=2, padx=5, pady=5)

        self._id = id
        self._name = name
        self._sensor_data = sensor_data
        self._details_dlg = None

    def _determine_background_color(self, sensor_data):
        """
        Apply all sensor checks to determine the background color of the widget
        :param sensor_data: Sensor data to be checked
        :return:
        """
        bg = self._config[Configuration.CFG_NORMAL_BACKGROUND_COLOR]

        # Time out check (elapsed time since last sensor data was received)
        dt = datetime.now() - sensor_data["timestamp"]
        if dt.seconds >= self._config[Configuration.CFG_OFFLINE_TIME]:
            bg = self._config[Configuration.CFG_OFFLINE_COLOR]

        # Low battery check
        if sensor_data["battery"] <= self._config[Configuration.CFG_LOW_BATTERY_THRESHOLD]:
            bg = self._config[Configuration.CFG_LOW_BATTERY_COLOR]

        return bg

    def _show_details(self, event):
        """
        Show all the current sensor readings
        :return:
        """
        self._details_dlg = SensorDetailsDlg(self, self._name, self._sensor_data)

    def update(self, sensor_data):
        """
        Update the displayed sensor values
        :param sensor_data: dict of sensor values
        :return:
        """
        self._sensor_data = sensor_data

        # Update sensor name and color
        self.config(text=sensor_data["name"])
        self.config(bg=self._determine_background_color(sensor_data))

        # Update sensor values
        for data_key, data_name in SensorWidget._SENSOR_VALUE_KEYS.items():
            bg = self._determine_background_color(sensor_data)
            self._sensor_labels[data_key].config(bg=bg)
            self._sensor_value_labels[data_key].config(bg=bg)
            self._sensor_value_labels[data_key].config(text=f"{sensor_data[data_key]:5.1f}")
