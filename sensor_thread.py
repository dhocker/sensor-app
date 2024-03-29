#
# sensor_thread.py - RuuviTag sensor data collection
# Copyright © 2022, 2023 Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#

from datetime import datetime
from threading import Thread, Lock
from json import dumps, dump
import logging
import copy
from configuration import Configuration
from sensor_utils import to_fahrenheit

from ruuvitag_sensor.ruuvi import RuuviTagSensor, RunFlag


class SensorThread(Thread):
    """
    This is a data receiver for RuuviTag sensor data.
    It runs on its own thread because of the way that the ruuvitag-sensor
    module works.
    """
    def __init__(self, handle_sensor_data=None):
        self._handle_sensor_data = handle_sensor_data
        self._data_point_count = 0
        self._runflag = RunFlag()
        self._logger = logging.getLogger("sensor_app")
        super().__init__()

        # Get access to the ruuvitags configuration (mac to name)
        self._config = Configuration.get_configuration()
        self._temperature_format = self._config[Configuration.CFG_TEMPERATURE_FORMAT].lower()

    def open(self):
        """
        Start data collection on the thread
        Returns:

        """
        self.start()

    def close(self):
        """
        Terminate the data collection thread. This method is intended to be
        called from another (e.g. the originating) thread.
        Returns:

        """
        self.terminate()
        self._logger.info("Waiting for SensorThread to terminate")
        self.join()

    def run(self):
        try:
            # Start receiving data from all sensors
            RuuviTagSensor.get_data(self._receive_sensor_data, run_flag=self._runflag)
            # NOTE that control does not return UNTIL the run_flag is set to False. See the terminate() method.
        except Exception as ex:
            self._logger.error("Unhandled exception caught in SensorThread.run()")
            self._logger.error(str(ex))
        finally:
            self._logger.info("RuuviTagSensor.get_data() ended")

    def _receive_sensor_data(self, received_data):
        """
        Handle sensor data
        :param received_data: a 2-tuple consisting of the mac and a dict.
        Reference: https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_05.md
        :return:
        """
        try:
            self._data_point_count += 1

            mac = received_data[0]
            data = received_data[1]

            # Make sure the mac is the same. The one in the data is lower case, no delimiters
            data["mac"] = mac

            # Record when the data was received
            data["timestamp"] = datetime.now()
            # Convert temperature as required
            if self._temperature_format == "f":
                data["temperature"] = to_fahrenheit(float(data["temperature"]))

            # Pass data sample to receiver/observer
            if self._handle_sensor_data is not None:
                self._handle_sensor_data(mac, data)

            # TODO Disable for release
            # self._logger.debug(f"Data received from {mac} {data['mac']}")
        except Exception as ex:
            self._logger.error("Unhandled exception caught in SensorThread._receive_sensor_data()")
            self._logger.error(str(ex))
        finally:
            pass

    def print_sensor_data(self, mac, data, dump_json=False):
        # Format lines to be printed/logged

        line_sen = str.format('Sensor:      {0}', mac)

        # line_tem = str.format('Temperature: {0} C', data['temperature'])
        line_tem = str.format('Temperature: {0:.2f} F', to_fahrenheit(data['temperature']))

        line_hum = str.format('Humidity:    {0:.2f} %', data['humidity'])

        line_pre = str.format('Pressure:    {0:.2f} hPa', data['pressure'])

        line_tod = f"TOD:         {str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}"
        line_count = f"Count:       {self._data_point_count}"

        # Print/log sensor data
        print(line_sen)
        print(line_tod)
        print(line_count)
        print(line_tem)
        print(line_hum)
        print(line_pre)
        if dump_json:
            print("\n\r")
            print(dumps(data, indent=4))
        print('.......')
        print('Press Ctrl+C to quit.\n\r\n\r')

    def terminate(self):
        """
        Terminate sensor data collection
        Returns: None
        """
        self._runflag.running = False
        self._logger.debug("SensorThread.run() is terminating...")
