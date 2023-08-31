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


import wx
from wx_utils import show_info_message
from sensor_db import SensorDB
from wx_sensor_history_dlg import SensorHistoryDlg


def show_sensor_history(sensor_widget):
    """
    Show the sensor history dialog. This is a graph of the last
    24 hours of sensor temperature data points.
    :param sensor_widget: The WX widget for the sensor.
    :return: None
    """
    data = sensor_widget.current_sensor_data
    db = SensorDB()
    dlg = wx.GenericProgressDialog(f"Sensor History", f"Querying database...")
    dlg.Pulse("Querying database...")
    sensor_history = db.get_sensor_history(data["mac"], progress_dlg=dlg)
    dlg.Destroy()

    if sensor_history is None or len(sensor_history) == 0:
        show_info_message(sensor_widget,
                          f"No history data for sensor {data['name']} {data['mac']}",
                          "View Sensor History")
    else:
        # Determine relative time (in seconds) of each data point
        start_time = sensor_history[0]["data_time"]
        for r in sensor_history:
            dt = r["data_time"] - start_time
            r["t"] = float((dt.days * 3600.0 * 24.0) + dt.seconds) / 3600.0

        dlg = SensorHistoryDlg(sensor_widget, data["name"], sensor_history)
        dlg.ShowModal()
