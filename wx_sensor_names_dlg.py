#
# wx_sensor_names_dlg.py - a dialog for managing sensor names
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE.md file for more details.
#


import logging
import wx
import wx.lib.scrolledpanel as scrolled
from wx_utils import show_info_message
from sensor_db import SensorDB


class SensorNamesDlg(wx.Dialog):
    """
    A custom dialog for displaying/editing sensor names
    """
    RESULT_SAVE = 1
    RESULT_CANCEL = 2

    def __init__(self, parent):
        """
        Create the sensor names dialog box
        @param parent: Parent of the dialog (usually a wx.Frame or wx.Window)
        """
        self._logger = logging.getLogger("sensor_app")

        # Layout
        self._border_width = 3
        # TODO Use system properties to determine sizes
        dlg_width = 400 + (self._border_width * 2)
        dlg_height = 400

        super().__init__(parent,
                         style=wx.RESIZE_BORDER | wx.DEFAULT_DIALOG_STYLE,
                         title=f"Sensor Names",
                         size=wx.Size(dlg_width, dlg_height))
        self.Center()

        # Add a panel so it looks the correct on all platforms
        self._dlg_panel = wx.Panel(self, wx.ID_ANY)
        self._dlg_panel_sizer = wx.BoxSizer(wx.VERTICAL)

        # Start with an empty grid
        self._scrolled_panel_sizer = None

        self._scrolled_panel = scrolled.ScrolledPanel(self._dlg_panel,
                                                      size=(dlg_width - 10, dlg_height - 70),
                                                      style=wx.TAB_TRAVERSAL | wx.SUNKEN_BORDER, name="Sensors")
        self._dlg_panel_sizer.Add(self._scrolled_panel, flag=wx.EXPAND | wx.BOTTOM, border=self._border_width)

        # Create the sensor list for editing
        self._sensor_widgets = None
        self._create_sensor_list()

        button_panel = self._create_button_panel(self._dlg_panel)
        self._dlg_panel_sizer.Add(button_panel, flag=wx.ALIGN_CENTER | wx.TOP | wx.BOTTOM, border=self._border_width)

        self._dlg_panel.SetSizer(self._dlg_panel_sizer)

        # Catch ESC
        self.Bind(wx.EVT_CHAR_HOOK, self._on_escape)

    def _create_sensor_list(self):
        """
        Create a flex grid list of sensors
        @return: None
        """

        # TODO Consider refactoring this out of the dialog (model/view concerns)
        # Get all the sensor table records
        db = SensorDB()
        sensor_list = db.get_all_sensor_records()

        # Reset existing grid sizer
        if self._scrolled_panel_sizer is not None:
            self._scrolled_panel_sizer.Clear(delete_windows=True)
        else:
            # Row count is the default allowing any number of rows
            self._scrolled_panel_sizer = wx.FlexGridSizer(0, 4,
                                                          int(self._border_width / 2),
                                                          int(self._border_width / 2))

        # Create sensor rows
        self._sensor_widgets = []
        self._create_header_item(self._scrolled_panel, self._scrolled_panel_sizer,
                                 "Id", "Sensor mac", "Name")
        for r in sensor_list:
            self._create_sensor_item(self._scrolled_panel, self._scrolled_panel_sizer,
                                     r["id"], r["mac"], r["name"])

        self._scrolled_panel.SetSizer(self._scrolled_panel_sizer)
        self._scrolled_panel.SetAutoLayout(1)
        self._scrolled_panel.SetupScrolling()

    def _create_sensor_item(self, parent, sizer, id, mac, name):
        """
        Create a sensor list item
        @param parent: The containing panel
        @param id:
        @param mac:
        @param name:
        @return:
        """
        id_widget = wx.StaticText(parent, label=f"{id}", style=wx.ALIGN_LEFT)
        sizer.Add(id_widget, flag=wx.EXPAND | wx.ALL, border=self._border_width)
        # box_sizer.AddSpacer(10)

        mac_widget = wx.StaticText(parent, label=f"{mac}", style=wx.ALIGN_LEFT)
        sizer.Add(mac_widget, flag=wx.EXPAND | wx.ALL, border=self._border_width)

        # Try to force a minimum size control
        name_widget = wx.TextCtrl(parent, value=f"{name}", style=wx.ALIGN_LEFT, size=(100, 15))
        sizer.Add(name_widget, flag=wx.EXPAND | wx.ALL, border=self._border_width)

        # Accumulate a list of sensor IDs and their respective text control
        self._sensor_widgets.append({"id": id, "name_widget": name_widget})

        delete_button = wx.Button(parent, int(id), label="Delete")
        sizer.Add(delete_button, flag=wx.EXPAND | wx.ALL, border=self._border_width)
        delete_button.Bind(wx.EVT_BUTTON, self._on_delete)

    def _create_header_item(self, parent, sizer, id, mac, name):
        """
        Create asensor list header
        @param parent: The containing parent
        @param id:
        @param mac:
        @param name:
        @return:
        """
        id_widget = wx.StaticText(parent, label=f"{id}", style=wx.ALIGN_LEFT)
        sizer.Add(id_widget, flag=wx.EXPAND | wx.ALL, border=self._border_width)

        mac_widget = wx.StaticText(parent, label=f"{mac}", style=wx.ALIGN_LEFT)
        sizer.Add(mac_widget, flag=wx.EXPAND | wx.ALL, border=self._border_width)

        name_widget = wx.StaticText(parent, label=f"{name}", style=wx.ALIGN_LEFT)
        sizer.Add(name_widget, flag=wx.EXPAND | wx.ALL, border=self._border_width)

        delete_widget = wx.StaticText(parent, label="-", style=wx.ALIGN_LEFT)
        sizer.Add(delete_widget, flag=wx.EXPAND | wx.ALL, border=self._border_width)

    def _create_button_panel(self, parent):
        """
        Create a panel containing all the dialog's buttons
        @param parent: The parent of the button panel
        @return:
        """
        self._button_panel = wx.Panel(parent)
        self._button_sizer = wx.BoxSizer(wx.HORIZONTAL)

        save_button = wx.Button(self._button_panel, 1001, label="Save")
        self._button_sizer.Add(save_button, flag=wx.ALIGN_CENTER | wx.ALL, border=self._border_width)
        # Catch the Save button
        self.Bind(wx.EVT_BUTTON, self._on_save, source=save_button)

        cancel_button = wx.Button(self._button_panel, 1002, label="Cancel")
        self._button_sizer.Add(cancel_button, flag=wx.ALIGN_CENTER | wx.ALL, border=self._border_width)
        # Catch the Cancel button
        self.Bind(wx.EVT_BUTTON, self._on_cancel, source=cancel_button)

        self._button_panel.SetSizer(self._button_sizer)

        return self._button_panel

    def _on_save(self, evt):
        """
        Save the sensor names
        @param evt: Not used
        @return: None
        """
        # TODO Save all sensors to DB
        self._logger.info("Sensor list saved")

        db = SensorDB()

        for s in self._sensor_widgets:
            new_name = s["name_widget"].GetValue()
            db.update_sensor_record(s["id"], new_name)

        del db

        self.EndModal(SensorNamesDlg.RESULT_SAVE)

    def _on_cancel(self, evt):
        """
        Save the sensor names
        @param evt: Not used
        @return: None
        """
        self._logger.info("Sensor list editing canceled")
        self.EndModal(SensorNamesDlg.RESULT_CANCEL)

    def _on_escape(self, evt):
        """
        Treat the ESC key like the Cancel button
        :param evt: Key event
        :return: None
        """
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self._on_cancel(evt)
            evt.Skip()
        else:
            # Continue handling the key
            evt.Skip(True)

    def _on_delete(self, evt):
        """
        Delete a sensor from the database. In practice, this is a low probability
        event. To successfully remove a sensor you must first disable the sensor
        by removing its battery. Otherwise, the sensor will continure to
        transmit data and the app will be quicly rediscovered and added to the
        list of known sensors.
        @param evt: evt.EventObject.Id is the record ID of the sensor record
        to be deleted.
        @return:
        """
        # evt.EventObject.Id has the sensor record ID
        self._logger.info(f"Sensor ID {evt.EventObject.Id} deleted")

        db = SensorDB()
        db.delete_sensor_record(evt.EventObject.Id)
        del db

        # The sensor was deleted
        show_info_message(self,
                          f"Sensor ID {evt.EventObject.Id} has been deleted",
                          "Sensor Deleted")

        # Refresh the sensor list
        self._create_sensor_list()
