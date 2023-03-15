#
# dummy_sensor_adapter.py - stub for testing without real sensor
# Copyright © 2022  Dave Hocker (email: AtHomeX10@gmail.com)
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


from time import sleep
from datetime import datetime
import random
import logging
import copy
from threading import Lock
from sensor_utils import to_fahrenheit
from configuration import Configuration


class DummySensorAdapter:
    """
    This class serves as both a test dummy and a base class for sensor adapters.
    """
    def __init__(self):
        self._terminate = False
        self._logger = logging.getLogger("sensor_monitor")
        self._list_lock = Lock()
        self._config = Configuration.get_configuration()
        self._dummy_ruuvi_data = {}

        self._generate_ruuvi_data()

    def _generate_ruuvi_data(self):
        """
        Generate dummy data for each tag defined in the configuration file
        :return:
        """
        for mac, kvn in self._config[Configuration.CFG_RUUVITAGS].items():
            # The mac appears without semicolons in the tag data
            mac_str = mac.replace(":", "")
            self._dummy_ruuvi_data[mac] = {
                "name": kvn["name"],
                "timestamp": datetime.now(),
                "data_format": 5,
                "humidity": 54.94,
                "temperature": to_fahrenheit(25.62),
                "pressure": 1008.72,
                "acceleration": 1018.2416216203303,
                "acceleration_x": -168,
                "acceleration_y": -24,
                "acceleration_z": 1004,
                "tx_power": 4,
                "battery": 3027,
                "movement_counter": 43,
                "measurement_sequence_number": 26017,
                "mac": mac_str,
                "rssi": -84,
                "sequence": 1,
            }

    def open(self):
        """
        Start data collection on the thread
        Returns:

        """
        pass

    def close(self):
        """
        Terminate the data collection thread. This method is intended to be
        called from another (e.g. the originating) thread.
        Returns:

        """
        pass

    @property
    def sensor_list(self):
        """
        Return the sensor list. Note that this should be treated as read-only data.
        Returns: The current sensor list. The sensor list is a dict whose
        key is the RuuviTag mac and the data is what the RuuviTagSensor module returned.
        The data is also a dict containing all the sensors properties.
        """
        # Update data. Pick up any settings changes.
        self._generate_ruuvi_data()
        return self._dummy_ruuvi_data

    def lock_sensor_list(self):
        """
        Acquire the list lock
        :return: Locked sensor list
        """
        # There is no lock for the dummy data
        self._list_lock.acquire()
        return self.sensor_list

    def unlock_sensor_list(self):
        """
        Release the list lock
        :return:
        """
        # There is no lock for the dummy data
        self._list_lock.release()

    def terminate(self):
        """
        Terminate sensor data collection
        Returns: None
        """
        self._logger.debug("DummySensorAdapter is terminating...")
        self._terminate = True
