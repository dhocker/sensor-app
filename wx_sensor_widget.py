#
# wx_sensor_widget.py - a displayable sensor widget's data
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


from datetime import datetime
import wx
# from sensor_details_dlg import SensorDetailsDlg
from configuration import Configuration
from wx_sensor_data_item import SensorDataItem
from wx_widget_popup_menu import WidgetPopupMenu


class SensorWidget(wx.StaticBox):
    """
    This widget is based on the StaticBox instead of Panel. The StaticBox is
    the closest wx widget to the TK LabelFrame. Unfortunately, it behaves
    subtly different.
    """
    # The values that will be displayed. The key and its label.
    _SENSOR_VALUE_KEYS = {
        "temperature": {"label": "temp", "suffix": "F"},
        "humidity": {"label": "humid", "suffix": "%"}
    }

    def __init__(self, parent, id, name, sensor_data, on_selected=None):
        """
        A widget representing a sensor
        :param parent: The parent panel
        :param id:
        :param name:
        :param sensor_data:
        :param on_selected:
        """
        self._parent = parent
        super().__init__(parent,
                         label=name,
                         style=wx.BORDER_DEFAULT,
                         size=wx.Size(25, 25))
        self._config = Configuration.get_configuration()
        self._widget_ctls = {}
        self._selected = False
        self._last_sensor_data = sensor_data
        self._on_selected_callback = on_selected

        # TODO Find a better way to highlight/display the sensor name
        # Change the wight of the base font to bold
        font = self.GetFont()
        font.Weight = wx.FONTWEIGHT_BOLD
        self.SetFont(font)

        # self._name = wx.StaticText(self, label=name, style=wx.ALIGN_CENTER_HORIZONTAL)
        widget_sizer = wx.BoxSizer(wx.VERTICAL)

        self._temp = SensorDataItem(self, "temp", f"{sensor_data['temperature']:5.1f}F")
        self._widget_ctls["temperature"] = self._temp

        self._humid = SensorDataItem(self, "humid", f"{sensor_data['humidity']:5.1f}%")
        self._widget_ctls["humidity"] = self._humid

        # Battery balue is milli-volts. Format to volts.
        bat_mv = float(sensor_data['battery'])/1000.0
        self._battery = SensorDataItem(self, "battery", f"{bat_mv:5.3f}v")
        self._widget_ctls["battery"] = self._battery

        last = SensorWidget._last_data_time(sensor_data['timestamp'])
        self._last = SensorDataItem(self, "last", f"{last:3d}s")
        self._widget_ctls["last"] = self._last

        # widget_sizer.Add(boxsizer)
        widget_sizer.Add(self._temp, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=5)
        widget_sizer.Add(self._humid, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=5)
        widget_sizer.Add(self._battery, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=5)
        widget_sizer.Add(self._last, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=5)

        self.SetSizer(widget_sizer)

        # Capture clicks on the widget
        self.Bind(wx.EVT_LEFT_UP, self._on_left_click)
        self.Bind(wx.EVT_RIGHT_UP, self._on_right_click)

    def _on_left_click(self, evt):
        """
        Handle a click on the widget
        @param evt: Not used
        @return: None
        """
        self._selected = not self._selected
        self.update(self._last_sensor_data)
        if self._on_selected_callback is not None:
            self._on_selected_callback(self, self._selected)

    def _on_right_click(self, evt):
        """
        On right click show the popup context menu
        :param evt: Noe used
        :return: None
        """
        popup = WidgetPopupMenu(self)
        self.PopupMenu(popup, evt.GetPosition())

    def select(self, selected=False):
        if self._selected != selected:
            self._selected = selected
            self.update(self._last_sensor_data)

    def update(self, sensor_data):
        """
        Update the displayed sensor values
        :param sensor_data: dict of sensor values
        :return:
        """
        self._last_sensor_data = sensor_data

        # Update sensor name and color
        bg = self._determine_background_color(sensor_data)
        # self._name.SetLabel(sensor_data["name"])
        self.SetBackgroundColour(bg)

        # Update box label
        self.SetLabel(sensor_data["name"])

        # Update sensor values
        for data_key, data_props in SensorWidget._SENSOR_VALUE_KEYS.items():
            self._widget_ctls[data_key].set_value(f"{sensor_data[data_key]:5.1f}{data_props['suffix']}")

        # Elapsed time since last data
        last = SensorWidget._last_data_time(sensor_data["timestamp"])
        self._last.set_value(f"{last:3d}s")

    @property
    def current_sensor_data(self):
        return self._last_sensor_data

    def _determine_background_color(self, sensor_data):
        """
        Apply all sensor checks to determine the background color of the widget
        :param sensor_data: Sensor data to be checked
        :return: Calculated background color
        """
        # The default background is based on the selected state
        if self._selected:
            bg = self._config[Configuration.CFG_SELECTED_BACKGROUND_COLOR]
        else:
            bg = self._config[Configuration.CFG_NORMAL_BACKGROUND_COLOR]

        # Time out check (elapsed time since last sensor data was received)
        dt = datetime.now() - sensor_data["timestamp"]
        if dt.seconds >= self._config[Configuration.CFG_OFFLINE_TIME]:
            bg = self._config[Configuration.CFG_OFFLINE_COLOR]

        # Low battery check
        if sensor_data["battery"] <= self._config[Configuration.CFG_LOW_BATTERY_THRESHOLD]:
            bg = self._config[Configuration.CFG_LOW_BATTERY_COLOR]

        return bg

    @staticmethod
    def _last_data_time(last_timestamp):
        """
        Calculate the time (in seconds) since the last update
        :param last_timestamp:
        :return:
        """
        delta = datetime.now() - last_timestamp
        return delta.seconds
