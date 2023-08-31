#
# wx_widget_popup_menu.py - context menu for a sensor widget
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
from wx_sensor_history import show_sensor_history
from wx_sensor_details_dlg import SensorDetailsDlg


class WidgetPopupMenu(wx.Menu):
    """
    Popup context menu for a sensor widget
    """
    def __init__(self, parent):
        """
        Popup context menu for a sensor widget
        :param parent: The sensor widget
        """
        super().__init__()

        self._parent = parent

        # Menu entries
        menu_item = wx.MenuItem(self, 100, 'View details ')
        self.Append(menu_item)
        self.Bind(wx.EVT_MENU, self._show_sensor_details, id=100)

        menu_item = wx.MenuItem(self, 101, 'View history ')
        self.Append(menu_item)
        self.Bind(wx.EVT_MENU, self._show_sensor_history, id=101)

    def _show_sensor_history(self, evt):
        """
        The the sensor's history
        :param evt: Not used
        :return: None
        """
        show_sensor_history(self._parent)

    def _show_sensor_details(self, evt):
        """
        Show the details of the last received widget data point
        :param evt: Not used
        :return: None
        """
        data = self._parent.current_sensor_data
        dlg = SensorDetailsDlg(self._parent, data)
        dlg.ShowModal()
