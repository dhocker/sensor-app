#
# WX Sensor App - wxPython RuuviTag sensor application
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# License: GPL v3. See LICENSE.md.
# This work is based on the original work documented below. It was
# intended for playing .mp3 files, but it will probably play any audio
# format the VLC supports (e.g. .wav files will play).
#


from configuration import Configuration
from wx_sensor_frame import SensorFrame
import wx
import logging
import app_logger
from wx_utils import set_menubar_app_name
from sensor_data_source_handler import SensorDataSourceHandler


if __name__ == "__main__":
    # Load configuration
    Configuration.load_configuration()

    # Start logging
    app_logger.start("sensor_app")
    logger = logging.getLogger("sensor_app")
    logger.info("sensor_app starting...")

    # Fix macos menu bar
    set_menubar_app_name("Sensor App")

    # Create the data source
    data_source = SensorDataSourceHandler()
    data_source.open_data_source()

    # Create a wx.App(), which handles the windowing system event loop
    app = wx.App(clearSigInt=True)  # XXX wx.PySimpleApp()
    # Create the window containing our media player
    main_frame = SensorFrame(app_name="WX_Sensor_App",
                             app_title="WX Sensor App",
                             data_source=data_source)
    # show the player window centred
    main_frame.Centre()
    main_frame.Show()

    # run the application
    app.MainLoop()

    # Clean up, save persistent configuration data
    try:
        # This will fail if the app is killed from the dock
        main_frame.on_close()
        data_source.close_data_source()
    except Exception as ex:
        logger.error("Did not run on_close")
        logger.error(str(ex))
        # Since on_close did not run, try to save the current configuration
        Configuration.save_configuration()

    logger.info("sensor_app ended")
