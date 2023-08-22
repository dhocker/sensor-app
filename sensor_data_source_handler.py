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
from threading import Lock


class SensorDataSourceHandler:
    def __init__(self):
        # Start up the sensor data DB
        self._sensor_db = SensorDB()
        self._config = Configuration.get_configuration()
        self._logger = logging.getLogger("sensor_app")
        self._sensor_data_source = None
        self._sensor_list = {}
        self._list_lock = Lock()
        self._pending_sensor_changes = False

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
        sensor_rec = self._sensor_db.add_sensor(mac)
        # Add the sensor name to the sensor data
        data["name"] = sensor_rec["name"]
        # Log to DB
        self._sensor_db.add_sensor_data(mac, data)

        # Record last data point for this sensor
        self.lock_sensor_list()
        self._sensor_list[mac] = data
        self._pending_sensor_changes = True
        self.unlock_sensor_list()

    def close_data_source(self):
        self._sensor_data_source.close()
        self._logger.info("Data source closed")

    def reset_sensor_list(self):
        """
        Reset the sensor list to allow a clean restart
        @return:
        """
        self._sensor_list = {}

    def lock_sensor_list(self):
        """
        Acquire the list lock
        :return: Locked sensor list
        """
        self._list_lock.acquire()
        return self._sensor_list

    def unlock_sensor_list(self):
        """
        Release the list lock
        :return:
        """
        self._list_lock.release()

    @property
    def pending_changes(self):
        """
        Answers the question: Is there unhandled sensor data
        :return: Returns True if there are pending sensor data changes
        """
        self._list_lock.acquire()
        c = self._pending_sensor_changes
        self._pending_sensor_changes = False
        self._list_lock.release()
        return c
