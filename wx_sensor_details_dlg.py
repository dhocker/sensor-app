#
# wx_sensor_details_dlg.py - a dialog for displaying all of a sensor's data
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE.md file for more details.
#


import wx
from wx_sensor_data_item import SensorDataItem


class SensorDetailsDlg(wx.Dialog):
    """
    A custom dialog for displaying sensor data in a list
    """
    def __init__(self, parent, sensor_data):
        """
        Create the dialog box
        @param parent: Parent of the dialog (usually a wx.Frame)
        @param sensor_data: A dict of the sensor's data
        """
        # Layout
        border_width = 10
        half_border_width = int(border_width / 2)
        c1_width = 220
        c2_width = 200
        dlg_width = c1_width + c2_width + (border_width * 2)
        dlg_height = 450
        lc_width = c1_width + c2_width - border_width
        lc_height = dlg_height - 50

        super().__init__(parent,
                         title=f"{sensor_data['name']} Sensor Details",
                         size=wx.Size(dlg_width, dlg_height))
        self.Center()

        widget_sizer = wx.BoxSizer(wx.VERTICAL)

        grid = wx.ListCtrl(self, style=wx.LC_REPORT, size=(lc_width, lc_height))
        grid.AppendColumn("Data Item", width=c1_width)
        grid.AppendColumn("Value", width=c2_width)

        # Show in alpha order
        for key in sorted(sensor_data.keys()):
            value = f"{sensor_data[key]:5.2f}" \
                if isinstance(sensor_data[key], float) \
                else str(sensor_data[key])
            # Append a new row to the list
            grid.Append([key, value])
        widget_sizer.Add(grid, 2, flag=wx.EXPAND | wx.LEFT | wx.RIGHT, border=half_border_width)

        # Space the dialog so the button is at the bottom
        widget_sizer.AddStretchSpacer()

        ok_button = wx.Button(self, 1, label="OK")
        widget_sizer.Add(ok_button, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=border_width)

        self.SetSizer(widget_sizer)

        # Catch the OK button
        self.Bind(wx.EVT_BUTTON, self._on_ok)

        # Catch ESC
        self.Bind(wx.EVT_CHAR_HOOK, self._on_escape)

    def _on_ok(self, evt):
        """
        Close the dialog
        @param evt: Not used
        @return: None
        """
        self.Close()

    def _on_escape(self, evt):
        """
        Treat the ESC key like the OK button
        :param evt: Key event
        :return: None
        """
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self._on_ok(evt)
            evt.Skip()


# class SensorDetailsDlgOG(wx.Dialog):
#     """
#     A custom dialog for sensor data
#     """
#     def __init__(self, parent, sensor_data):
#         """
#         Create the dialog box
#         @param parent: Parent of the dialog (usually a wx.Frame)
#         @param sensor_data: A dict of the sensor's data
#         """
#         super().__init__(parent, title=f"{sensor_data['name']} Sensor Details", size=wx.Size(300, 350))
#
#         widget_sizer = wx.BoxSizer(wx.VERTICAL)
#
#         for key in sorted(sensor_data.keys()):
#             value = f"{sensor_data[key]:5.2f}" if isinstance(sensor_data[key], float) else sensor_data[key]
#             item = SensorDataItem(self, key, value)
#             widget_sizer.Add(item, flag=wx.LEFT | wx.RIGHT | wx.EXPAND, border=5)
#
#         # Space the dialog so the button is at the bottom
#         widget_sizer.AddStretchSpacer()
#
#         ok_button = wx.Button(self, 1, label="OK")
#         widget_sizer.Add(ok_button, flag=wx.ALIGN_CENTER | wx.BOTTOM, border=10)
#
#         self.SetSizer(widget_sizer)
#
#         # Catch the OK button
#         self.Bind(wx.EVT_BUTTON, self._on_ok)
#
#     def _on_ok(self, evt):
#         """
#         Close the dialog
#         @param evt: Not used
#         @return: None
#         """
#         self.Close()
