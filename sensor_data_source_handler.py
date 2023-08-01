#
# sensor_data_source_handler.py - Handles received sensor data
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


from configuration import Configuration
from sensor_db import SensorDB
import logging


class SensorDataSourceHandler:
    def __init__(self):
        # Start up the sensor data DB
        self._sensor_db = SensorDB()
        self._config = Configuration.get_configuration()
        self._logger = logging.getLogger("sensor_app")
        self._sensor_data_source = None

    def open_data_source(self):
        # Trim aged data records
        self._sensor_db.trim_sensor_data()

        # Start sensor data source
        if self._config[Configuration.CFG_USE_TEST_DATA].lower() == "true":
            from dummy_sensor_adapter import DummySensorAdapter as SensorThread
        else:
            from sensor_thread import SensorThread
        self._sensor_data_source = SensorThread(handle_sensor_data=self._handle_sensor_data)
        self._sensor_data_source.open()
        self._logger.info("Data source opened")

    def _handle_sensor_data(self, mac, data):
        """
        Handle (log) a sensor data sample
        :param mac: The mac of the sensor
        :param data: A dict of sensor data keys and values
        :return: None
        """
        # print(f"Handling data for mac: {mac}")
        self._sensor_db.add_sensor(mac, data["name"])
        self._sensor_db.add_sensor_data(mac, data)

    def close_data_source(self):
        self._sensor_data_source.close()
        self._logger.info("Data source closed")

    def lock_sensor_list(self):
        return self._sensor_data_source.lock_sensor_list()

    def unlock_sensor_list(self):
        self._sensor_data_source.unlock_sensor_list()
