#
# wx_sensor_item.py - a custom row to hold sensor data
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


import wx


class SensorDataItem(wx.Panel):
    BORDER_WIDTH = 3

    def __init__(self, parent, label, value):
        """
        Create a sensor data item widget. The data item has a label and a value.
        The label is left justified and the value is right justified
        @param parent: Parent of the widget, usually a Panel
        @param label: Data item label.
        @param value: Data item value (should be a string).
        """
        super().__init__(parent)

        self._box_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self._label_widget = wx.StaticText(self, label=label, style=wx.ALIGN_LEFT)
        self._box_sizer.Add(self._label_widget,
                            flag=wx.ALL | wx.EXPAND, border=self.BORDER_WIDTH)

        # This inserts space between the label and the value causing them to left/right align
        self._box_sizer.AddStretchSpacer()

        self._value_widget = wx.StaticText(self, label=f"{value}", style=wx.ALIGN_RIGHT)
        self._box_sizer.Add(self._value_widget,
                            flag=wx.ALL | wx.EXPAND, border=self.BORDER_WIDTH)

        self.SetSizer(self._box_sizer)

    def set_value(self, value):
        """
        Update the value of the sensor data item (which is a StaticText box.
        @param value: New value for the data item (should be a string).
        @return: None
        """
        self._value_widget.SetLabel(value)
