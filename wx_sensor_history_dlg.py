#
# wx_sensor_history_dlg.py - a dialog for displaying all of a sensor's history
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE.md file for more details.
#
# Some of this code was adapted from the how-to article at
# https://wiki.wxpython.org/How%20to%20use%20Plot%20-%20Part%201%20%28Phoenix%29
#


import wx
from wx.lib import plot as wxplot


class SensorHistoryDlg(wx.Dialog):
    """
    A custom dialog for displaying sensor data in a list
    """
    def __init__(self, parent, name, sensor_data):
        """
        Create the dialog box
        @param parent: Parent of the dialog (usually a wx.Frame)
        @param name: Sensor's human-readable name
        @param sensor_data: A list of sensor data points.
        Each data point is a dict of the sensor's data.
        """
        # Layout
        border_width = 10
        half_border_width = int(border_width / 2)
        dlg_width = 600 + (border_width * 2)
        dlg_height = 450
        gr_width = dlg_width - 10
        gr_height = int(dlg_height * .85)
        last_data_point = len(sensor_data) - 1

        super().__init__(parent,
                         title=f"{name} Sensor History",
                         size=wx.Size(dlg_width, dlg_height))

        widget_sizer = wx.BoxSizer(wx.VERTICAL)

        # Build plot here

        # Generate x, y lists of data points
        x_time_data = []
        y_value_data = []
        for r in sensor_data:
            x_time_data.append(r["t"])  # t is the data point time
            y_value_data.append(r["temperature"])  # the data point value

        # Most items require data as a list of (x, y) pairs:
        #    [[x1, y1], [x2, y2], [x3, y3], ..., [xn, yn]]
        xy_data = list(zip(x_time_data, y_value_data))

        # Create your Poly object(s).
        # Use keyword args to set display properties.
        line = wxplot.PolySpline(
            xy_data,
            colour=wx.Colour(255, 0, 0),   # Color: red
            width=1,
        )

        # Create your graphics object.
        plot_graphics = wxplot.PlotGraphics([line])

        # Create your canvas.
        plot_canvas = wxplot.PlotCanvas(self, size=wx.Size(gr_width, gr_height))

        # Edit panel-wide settings.
        axes_pen = wx.Pen(wx.BLACK, 1, wx.PENSTYLE_SOLID)
        plot_canvas.axesPen = axes_pen

        # Draw the graphics object on the canvas.
        plot_canvas.Draw(plot_graphics)

        # Layout the widgets.
        widget_sizer.Add(plot_canvas, 1, wx.EXPAND | wx.ALL, 10)

        # Display time range
        start_time = sensor_data[0]['data_time'].strftime("%Y-%m-%d %H:%M:%S")
        end_time = sensor_data[last_data_point]['data_time'].strftime("%Y-%m-%d %H:%M:%S")
        text = f"Start: {start_time}\t\t\t\t\t\t\tEnd: {end_time}"
        range_widget = wx.StaticText(self, label=f"{text}", style=wx.ALIGN_LEFT)
        widget_sizer.Add(range_widget,
                         flag=wx.ALIGN_TOP | wx.TOP | wx.BOTTOM | wx.LEFT | wx.RIGHT | wx.EXPAND,
                         border=10)

        # Space the dialog so the button is at the bottom
        widget_sizer.AddStretchSpacer()

        ok_button = wx.Button(self, 1, label="OK")
        widget_sizer.Add(ok_button, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=border_width)

        self.SetSizer(widget_sizer)

        # Catch the OK button
        self.Bind(wx.EVT_BUTTON, self._on_ok)

    def _on_ok(self, evt):
        """
        Close the dialog
        @param evt: Not used
        @return: None
        """
        self.Close()
