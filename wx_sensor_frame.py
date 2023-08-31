#
# WX Sensor Frame - wxPython main window for app
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files, but it will probably play any audio
# format the VLC supports (e.g. .wav files will play).
#


import datetime
import logging
from configuration import Configuration
from wx_utils import show_info_message, show_error_message
import wx
from wx_sensor_widget import SensorWidget
from wx_sensor_details_dlg import SensorDetailsDlg
from wx_sensor_history_dlg import SensorHistoryDlg
from wx_sensor_names_dlg import SensorNamesDlg
from sensor_db import SensorDB
from wx_sensor_history import show_sensor_history

# import standard libraries
from os.path import basename, join as joined


class SensorFrame(wx.Frame):
    """
    The frame contains a single panel which in turn contains all of the
    sensor widgets. The menubar is also part of the frame.
    """
    SENSOR_UPDATE_TIMER_ID = 1
    TRIM_DB_TIMER_ID = 2

    def __init__(self, app_name="WX_Sensor_App",
                 app_title="WX Sensor Monitor Ap",
                 data_source=None):
        """
        Main window for the sensor app
        :param app_name: The app's technical name
        :param app_title: The app's human-readable title
        :param data_source: The sensor data source instance
        """
        self._app_name = app_name
        self._app_title = app_title
        self._sensor_data_source = data_source
        self._logger = logging.getLogger("sensor_app")
        self._sensor_widgets = {}
        self._selected_sensor_widget = None

        self._config = Configuration.get_configuration()
        self._sensor_update_interval_ms = int(self._config[Configuration.CFG_UPDATE_INTERVAL] * 1000)

        # Determine display geometry
        display = wx.Display()
        client_rect = display.GetClientArea()
        width = client_rect.width
        height = client_rect.height
        self._logger.info(f"Display size {width} x {height}")
        # Limit size to RPi display panel
        maximize_frame = False
        if width > 800:
            width = 800
        if height > 480:
            height = 480
        self._logger.info(f"Adjusted frame size {width} x {height}")

        super().__init__(None,
                         id=-1,
                         title=self._app_title,
                         pos=(400, 300),
                         size=(width, height))

        # Create a logger
        self._logger = logging.getLogger("sensor_app")

        self._create_widgets()

        # Create the panel that will hold the sensor widgets
        self._panel = wx.Panel(self)
        self._sizer = wx.BoxSizer(wx.VERTICAL)
        self._sizer.Add(self._panel, 1, wx.EXPAND, 5)

        # Handle frame close via closer
        self.Bind(wx.EVT_CLOSE, self._on_close_frame)

        # Get number of cols from config
        self._sizer_cols = int(self._config["sensors_per_row"])
        self._panel_sizer = wx.GridSizer(self._sizer_cols, wx.Size(5, 5))

        self._panel.SetSizer(self._panel_sizer)
        self.SetSizer(self._sizer)

        # Start fielding sensor updates
        self._sensor_update_timer = wx.Timer(self, SensorFrame.SENSOR_UPDATE_TIMER_ID)
        self._sensor_update_timer.Start(self._sensor_update_interval_ms, oneShot=wx.TIMER_CONTINUOUS)
        self._update_sensors()

        # Start trimming DB
        self._trim_db_timer = wx.Timer(self, SensorFrame.TRIM_DB_TIMER_ID)
        self._trim_db_timer.Start(60 * 1000, oneShot=wx.TIMER_CONTINUOUS)  # every minute

        # Handle all timer events
        self.Bind(wx.EVT_TIMER, self._route_timer_events)

        # Capture clicks inside the container panel
        self._panel.Bind(wx.EVT_LEFT_UP, self._on_click)

    def _create_widgets(self):
        self._create_menubar()

    def _create_menubar(self):
        """
        Create the app menu bar. On macOS the menu bar is at the top of the
        screen. On Windows and Linux it is at the top of the frame/window.
        :return: None
        """
        self._frame_menubar = wx.MenuBar()

        #   File Menu
        self._file_menu = wx.Menu()
        self._file_menu.Append(1, "&Close", "Quit")
        self.Bind(wx.EVT_MENU, self._on_close_frame, id=1)

        # PLace holder edit menu
        self._edit_menu = wx.Menu()
        self._edit_menu.Append(10, "&Sensor names", "Sensor names")
        self.Bind(wx.EVT_MENU, self._edit_sensor_names, id=10)

        # TODO Sensor views
        self._view_menu = wx.Menu()
        self._view_menu.Append(20, "Sensor &details", "Sensor details")
        self.Bind(wx.EVT_MENU, self._show_selected_sensor_details, id=20)
        self._view_menu.Append(21, "Sensor &history", "Sensor history")
        self.Bind(wx.EVT_MENU, self._show_sensor_history, id=21)
        # self._view_menu.Append(22, "&Sensor names", "Sensor names")
        # self.Bind(wx.EVT_MENU, self._edit_sensor_names, id=22)

        # Complete the menu bar
        self._frame_menubar.Append(self._file_menu, "&File")
        self._frame_menubar.Append(self._edit_menu, "&Edit")
        self._frame_menubar.Append(self._view_menu, "&View")
        self.SetMenuBar(self._frame_menubar)

        # OS dependent menu
        os_id = wx.PlatformInformation.Get().GetOperatingSystemId()
        if os_id == wx.OS_MAC_OSX_DARWIN:
            # Special handling for the OSX menu
            osx_menu = self._frame_menubar.OSXGetAppleMenu()
            about_menuitem = wx.MenuItem(osx_menu, 999, f"About {self._app_name}")
            osx_menu.Insert(0, about_menuitem)
            self.Bind(wx.EVT_MENU, self._show_about_dlg, id=999)
            settings_menuitem = wx.MenuItem(osx_menu, 998, "Preferences")
            osx_menu.Insert(1, settings_menuitem)
            self.Bind(wx.EVT_MENU, self._show_settings, id=998)
        elif os_id == wx.OS_WINDOWS_NT:
            # Windows gets its own Help menu item
            self._help_menu = wx.Menu()
            self._help_menu.Append(900, "&About", f"About {self._app_name}")
            self._frame_menubar.Append(self._help_menu, "&Help")
            self.Bind(wx.EVT_MENU, self._show_about_dlg, id=900)
        else:
            # TODO Create Help/About menu/item for other OSes
            pass

    def _route_timer_events(self, evt):
        """
        Route timer events to their respective handlers
        @param evt:
        @return:
        """
        timer_id = evt.Id
        if timer_id == SensorFrame.SENSOR_UPDATE_TIMER_ID:
            self._update_sensors()
        elif timer_id == SensorFrame.TRIM_DB_TIMER_ID:
            self._trim_sensor_db()

    def _on_click(self, evt):
        """
        Left button clicked inside the container panel
        :param evt: Not used
        :return: None
        """
        # Unselect all
        # In the future we might need multi-select, but for now we only do single select
        for mac, widget in self._sensor_widgets.items():
            widget.select(selected=False)

        # Remember the last selected widget
        self._selected_sensor_widget = None

        self._update_sensors()

    def _trim_sensor_db(self):
        """
        Every hour trim the sensor DB
        :return:
        """
        self._logger.debug("Checking for DB trim")
        # On the hour, trim the database
        now = datetime.datetime.now()
        if now.minute == 0:
            self._logger.debug("Starting DB trimming")
            db = SensorDB()
            db.trim_sensor_data()

    def _create_sensor_frame(self, mac, sensor_data):
        sensor_frame = SensorWidget(self._panel, mac, sensor_data["name"], sensor_data,
                                    on_selected=self._on_sensor_widget_selected)
        self._sensor_widgets[mac] = sensor_frame

    def _create_sorted_mac_list(self, sensor_list):
        """
        Make a dict of just the mac and sensor name
        :param sensor_list: dict of sensor macs and associated sensor data
        :return: dict of sensor macs and their names
        """
        unsorted_mac_list = {}
        for mac, sensor_data in sensor_list.items():
            unsorted_mac_list[mac] = sensor_data["name"]

        # Sort the unsorted dict to a bunch of tuples
        sorted_mac_list = sorted(unsorted_mac_list.items(), key=lambda x:x[1])
        result_list = dict(sorted_mac_list)

        return result_list

    def _update_sensors(self):
        """
        Update the entire sensor frame display area
        :return:
        """
        self._logger.debug("Updating sensor frames")

        # Safely access the current sensor list
        sensor_list = self._sensor_data_source.lock_sensor_list()

        # Create newly discovered sensors
        refresh_req = False
        for mac, sensor_data in sensor_list.items():
            if mac not in self._sensor_widgets.keys():
                self._create_sensor_frame(mac, sensor_data)
                refresh_req = True

        # Create an ordered list of sensor macs so we can display them alphabetically by name
        sorted_mac_list = self._create_sorted_mac_list(sensor_list)

        # Order widgets by name, reposition all widgets
        if refresh_req:
            self._panel_sizer.Clear()
            rows = int(len(sorted_mac_list) / self._sizer_cols)
            if (len(sorted_mac_list) % self._sizer_cols) > 0:
                rows += 1
            self._panel_sizer.SetRows(rows)
            for mac in sorted_mac_list:
                self._panel_sizer.Add(self._sensor_widgets[mac], 1,
                                      flag=wx.EXPAND | wx.LEFT | wx.RIGHT | wx.TOP | wx.BOTTOM, border=5)
            self._panel_sizer.Layout()

        # Update sensor data in each frame
        for mac, sensor_data in sensor_list.items():
            self._sensor_widgets[mac].update(sensor_data)

        # Release the sensor list lock
        self._sensor_data_source.unlock_sensor_list()

    def _on_sensor_widget_selected(self, sensor_widget, widget_state):
        # Unselect all but the newly selected widget
        # In the future we might need multi-select, but for now we only do single select
        for mac, widget in self._sensor_widgets.items():
            if widget != sensor_widget:
                widget.select(selected=False)

        # Remember the last selected widget
        self._selected_sensor_widget = sensor_widget if widget_state else None

        self._update_sensors()

    def on_close(self):
        """
        Save app state at close
        :return: None
        """
        pass

    def _on_close_frame(self, event):
        """
        Handle frame closed by menu item or closer button
        :param event: Not used
        :return: None
        """
        self.on_close()
        self.Destroy()

    def _show_about_dlg(self, evt):
        """
        Show the "about" dialog with app version
        :param evt:
        :return:
        """
        show_info_message(self, "About placeholder", f"About {self._app_name}")

    def _show_settings(self, evt):
        """
        Bring up the settings window overtop of the main window
        :return:
        """
        show_info_message(self, "Settings/preferences is not implemented", "Settings/Preferences")

    def _show_selected_sensor_details(self, evt):
        """
        Show the sensor details dialog. This is a list of the values
        from the last received data point.
        :param evt: Not used
        :return: None
        """
        data = self._selected_sensor_widget.current_sensor_data
        dlg = SensorDetailsDlg(self, data)
        dlg.ShowModal()

    def _show_sensor_history(self, evt):
        """
        Show the sensor history dialog. This is a graph of the last
        24 hours of sensor temperature data points.
        :param evt: Not used
        :return: None
        """
        # A sensor must be selected
        if self._selected_sensor_widget is None:
            show_error_message(self,
                               "No sensor is selected",
                               "View Sensor History")
            return

        show_sensor_history(self._selected_sensor_widget)

    def _edit_sensor_names(self, evt):
        """
        Show the Edit Sensor Names dialog
        :param evt: Not used
        :return: None
        """
        dlg = SensorNamesDlg(self)
        result = dlg.ShowModal()

        if result == SensorNamesDlg.RESULT_SAVE:
            # Refresh sensor display to show changed names and deletions
            # Currently, this does not remove deleted sensors from the display
            self._panel_sizer.Clear(delete_windows=True)
            self._panel_sizer.Layout()
            self._sensor_widgets = {}
            self._sensor_data_source.reset_sensor_list()
            self._update_sensors()
