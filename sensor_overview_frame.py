#
# sensor_overview_frame.py - Overview of all RuuviTag sensors
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
from tkinter import Tk, Button, Label, Menu, Frame
from tkinter import font
from configuration import Configuration
import logging
from sensor_widget import SensorWidget


class SensorOverviewFrame(Frame):
    def __init__(self, parent, sensor_data_source=None, width=800, height=480):
        super(SensorOverviewFrame, self).__init__(width=width, height=height)
        self._parent = parent
        self._sensor_data_source = sensor_data_source

        # Create a logger
        self._logger = logging.getLogger("sensor_app")

        # Get the configuration
        self._config = Configuration.get_configuration()
        # The update interval is in milliseconds
        self._update_interval = int(self._config[Configuration.CFG_UPDATE_INTERVAL] * 1000.0)
        # Number of sensors to put on a row
        self._available_width = 5
        if Configuration.CFG_SENSORS_PER_ROW in self._config.keys():
            self._available_width = self._config[Configuration.CFG_SENSORS_PER_ROW]

        # Window metrics
        sw = width
        sh = height
        self._logger.info(f"Window size: {sw}x{sh}")

        # ttk theme
        # s = ttk.Style()
        # s.theme_use('classic')
        self.background_color = "#ffffff"
        self.highlight_color = "#e0e0e0"

        # Create window widgets
        self._quit_button = None
        self._current_time_label = None
        self._sensor_frames = {}
        self._gr = 0
        self._gc = 0
        self._create_widgets(sw, sh)

    def _create_widgets(self, sw, sh):
        # Create initial set of sensor widgets
        self.update_sensors()

    def _create_sensor_frame(self, mac, sensor_data):
        sensor_frame = SensorWidget(self, mac, sensor_data["name"], sensor_data)
        self._sensor_frames[mac] = sensor_frame

    def _create_sorted_mac_list(self, sensor_data):
        # Make a dict of just the mac and sensor name
        unsorted_mac_list = {}
        for mac, sensor_data in self._sensor_data_source.sensor_list.items():
            unsorted_mac_list[mac] = sensor_data["name"]

        # Sort the unsorted dict to a bunch of tuples
        sorted_mac_list = sorted(unsorted_mac_list.items(), key=lambda x:x[1])
        result_list = dict(sorted_mac_list)

        return result_list

    def update_sensors(self):
        """
        Update the entire sensor frame display area
        :return:
        """
        self._logger.debug("Updating sensor frames")

        # Create newly discovered sensors
        for mac, sensor_data in self._sensor_data_source.sensor_list.items():
            if mac not in self._sensor_frames.keys():
                self._create_sensor_frame(mac, sensor_data)

        # Create an ordered list of sensor macs so we can display them alphabetically by name
        sorted_mac_list = self._create_sorted_mac_list(self._sensor_data_source.sensor_list)

        self._gr = 0
        self._gc = 0

        # Show current time at the top right
        if self._current_time_label is None:
            dt_font = font.Font(family="Arial", size=18)
            self._current_time_label = Label(self, text=SensorOverviewFrame._now_str(), font=dt_font)
        else:
            self._current_time_label.config(text=SensorOverviewFrame._now_str())
        self._current_time_label.grid(row=self._gr,
                                      column=self._gc, columnspan=self._available_width,
                                      sticky="e",
                                      padx=10, pady=10)
        self._gr += 1

        # Order frames by name, reposition all frames
        self._available_width = self._config[Configuration.CFG_SENSORS_PER_ROW]
        for mac in sorted_mac_list:
            self._sensor_frames[mac].grid(row=self._gr, column=self._gc, padx=5, pady=5)
            self._available_width -= 1
            # See if another frame will fit in the current row
            if self._available_width <= 0:
                self._available_width = self._config[Configuration.CFG_SENSORS_PER_ROW]
                self._gr += 1
                self._gc = 0
            else:
                self._gc += 1

        # Update sensor data in each frame
        for mac, sensor_data in self._sensor_data_source.sensor_list.items():
            self._sensor_frames[mac].update(sensor_data)
        self._gr += 1

        # configuration setting
        self.after(self._update_interval, self.update_sensors)

    @staticmethod
    def _now_str():
        """
        Return a formatted string containing the current date and time
        :return:
        """
        now_dt = datetime.datetime.now()
        # custom format to remove unwanted leading zeros
        ampm = "am"
        if now_dt.hour >= 12:
            ampm = "pm"
        hour = now_dt.hour
        if hour > 12:
            hour -= 12
        return f"{now_dt.year:4d}-{now_dt.month:02d}-{now_dt.day:02d}  {hour:2d}:{now_dt.minute:02d} {ampm}"
