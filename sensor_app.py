# coding: utf-8
#
# Copyright © 2022, 2023 Dave Hocker (email: AtHomeX10@gmail.com)
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
# Icons
# https://stackoverflow.com/questions/12306223/how-to-manually-create-icns-files-using-iconutil
#


import datetime
from tkinter import messagebox
from tkinter import Tk, Button, Label, Menu
from tkinter import font
# from tkinter import ttk
from configuration import Configuration
import logging
import app_logger
from sensor_overview_frame import SensorOverviewFrame
from settings_frame import SettingsFrame
from tkmacos_utils import set_menubar_app_name
from display_controller import DisplayController


class SensorApp(Tk):
    def __init__(self):
        super(SensorApp, self).__init__()
        self.title("Ruuvi Tag Sensor App")

        # Create a logger
        self._logger = logging.getLogger("sensor_app")

        # Get the configuration
        self._config = Configuration.get_configuration()

        # Screen metrics
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self._logger.info(f"Full screen resolution: {sw}x{sh}")

        # Position and size main window
        fw = sw
        fh = sh
        if sw > 800:
            fw = 800
            fh = 480
        self._sw = fw
        self._sh = fh

        # ttk theme
        # s = ttk.Style()
        # s.theme_use('classic')
        self.background_color = "#ffffff"
        self.highlight_color = "#e0e0e0"

        # will return x11 (Linux), win32 or aqua (macOS)
        self._gfx_platform = self.tk.call('tk', 'windowingsystem').lower()

        # Maximize the window
        if self._gfx_platform in ["win32", "aqua"]:
            self.state("zoomed")
        elif self._gfx_platform == "x11":
            self.attributes("-zoomed", True)
        else:
            geo = "{0}x{1}+{2}+{3}".format(int(fw), int(fh), int(0), int(0))
            self.geometry(geo)
            self.resizable(width=False, height=False)

        # Start sensor data source
        if self._config[Configuration.CFG_USE_TEST_DATA].lower() == "true":
            from dummy_sensor_adapter import DummySensorAdapter as SensorThread
        else:
            from sensor_thread import SensorThread
        self._sensor_data_source = SensorThread()
        self._sensor_data_source.open()

        # Create menu
        self._create_menu()

        # Create overview frame
        self._overview_frame = SensorOverviewFrame(self,
                                                   sensor_data_source=self._sensor_data_source,
                                                   width=fw,
                                                   height=fh)
        # self._overview_frame.pack(side="top", fill="both", expand=True)
        self._overview_frame.grid(row=0, column=0, sticky="nsew")

        # Handle app exit (when the closer X is clicked)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # Display/backlight controller
        self._display_controller = DisplayController(count_down_time=self._config[Configuration.CFG_DISPLAY_TIMEOUT],
                                                     brightness=self._config[Configuration.CFG_DISPLAY_BRIGHTNESS])
        self._display_controller.reset_count_down()
        self._count_down_time = 10
        self.after(self._count_down_time * 1000, self._update_backlight_controller)

        # Capture events that reset the backlight timer
        # Only motion in the overview frame
        self._overview_frame.bind("<Motion>", self._reset_backlight_controller)
        # Any key like ctrl or alt
        self.bind("<Key>", self._reset_backlight_controller)

    def _create_menu(self):
        # App menu bar
        menu_font = font.Font(family="Arial", size=14)
        self._menu_bar = Menu(self, font=menu_font)

        # macOS app menu covering things specific to macOS
        if self._gfx_platform == "aqua":
            self._appmenu = Menu(self._menu_bar, name='apple')
            self._appmenu.add_command(label='About sensor-app', command=self._show_about)
            self._appmenu.add_separator()
            self._menu_bar.add_cascade(menu=self._appmenu, label='sensor-app')

            self.createcommand('tk::mac::ShowPreferences', self._show_settings)

        # All OSes
        filemenu = Menu(self._menu_bar, tearoff=0, font=menu_font)
        self._menu_bar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Quit", command=self.destroy)
        editmenu = Menu(self._menu_bar, tearoff=0, font=menu_font)
        self._menu_bar.add_cascade(label="Edit", menu=editmenu)

        # Non-macOS
        if self._gfx_platform in ["x11", "linux"]:
            # On macOS settings on the app menu. On all others, its on the edit menu
            editmenu.add_command(label="Settings", command=self._show_settings)
            helpmenu = Menu(self._menu_bar, tearoff=0, font=menu_font)
            helpmenu.add_command(label="About...", command=self._show_about)
            self._menu_bar.add_cascade(label="Help", menu=helpmenu)

        self.config(menu=self._menu_bar)

    def _update_backlight_controller(self):
        # Backlight time out interval is 10 seconds
        self._display_controller.count_down(self._count_down_time)
        self.after(10000, self._update_backlight_controller)

    def _reset_backlight_controller(self, event):
        self._display_controller.reset_count_down()

    def _show_settings(self):
        """
        Bring up the settings window overtop of the main window
        :return:
        """
        settings_frame = SettingsFrame(self, width=self._sw, height=self._sh)
        settings_frame.grid(row=0, column=0, sticky="nsew")
        settings_frame.tkraise()

    def update_frame(self):
        """
        Callback for children to force update of sensor widgets
        :return:
        """
        self._overview_frame.update_sensors()
        self._logger.debug("Sensor overview frame refreshed")

    def _show_about(self):
        # about_text = \
        #     "Copyright © 2022 by Dave Hocker\n" + \
        #     "\n" + \
        #     "Source: https://github.com/dhocker/pyid3tag\n" + \
        #     "License: GNU General Public License v3\n" + \
        #     "as published by the Free Software Foundation, Inc."
        #
        # # Locate logo image file
        # cwd = os.path.realpath(os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
        # if os.path.exists(cwd + "/id3tag.gif"):
        #     image_path = cwd + "/id3tag.gif"
        # elif os.path.exists(cwd + "/resources/id3tag.gif"):
        #     image_path = cwd + "/resources/id3tag.gif"
        # else:
        #     image_path = "id3tag.gif"
        #
        # # This is a modal message box
        # mb = TextMessageBox(self, title="About pyid3tag", text=about_text,
        #                     heading="ID3 Tag Editor",
        #                     image=image_path, orient=tkinter.HORIZONTAL)
        # mb.show()
        # self.wait_window(window=mb)
        messagebox.showinfo(title="About Sensor-App",
                            message="About for Sensor-App is not implemented",
                            parent=self)

    def _show_app_help(self):
        pass

    def destroy(self):
        """
        Override base class so we can terminate the sensor data collection thread.
        :return:
        """
        self._on_close()

    def _on_close(self):
        """
        App is closing. Warn user if unsaved changes.
        :return:
        """
        # Shutdown sensor data thread
        self._sensor_data_source.close()
        super(SensorApp, self).destroy()
        return True


if __name__ == '__main__':
    Configuration.load_configuration()
    # Start logging
    app_logger.start("sensor_app")
    logger = logging.getLogger("sensor_app")
    logger.info("sensor_app starting...")

    # Fix macos menu bar
    set_menubar_app_name("Sensor App")

    main_frame = SensorApp()
    main_frame.mainloop()
