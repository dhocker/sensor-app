#
# dummy_sensor_adapter.py - stub for testing without real sensor
# Copyright © 2022, 2023  Dave Hocker (email: AtHomeX10@gmail.com)
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
from datetime import datetime, timedelta
import random
import logging
from time import sleep
from threading import Thread
from sensor_utils import to_fahrenheit
from configuration import Configuration


class DummySensorAdapter(Thread):
    """
    This class serves as both a test dummy and a base class for sensor adapters.
    """
    def __init__(self, handle_sensor_data=None):
        self._handle_sensor_data = handle_sensor_data
        self._terminate = False
        self._logger = logging.getLogger("sensor_app")
        self._config = Configuration.get_configuration()
        self._sensor_list = []
        # Keyed by mac
        self._sensor_data_control = {}
        random.seed()

        super().__init__()

    def _generate_ruuvi_data(self, mac):
        """
        Generate dummy data for a single ruuvi tag
        :return:
        """
        data = {
            "name": "",
            "timestamp": self._random_timestamp(),
            "data_format": 5,
            "humidity": self._random_humid(mac),
            "temperature": to_fahrenheit(self._random_temp(mac)),
            "pressure": 1008.72,
            "acceleration": 1018.2416216203303,
            "acceleration_x": -168,
            "acceleration_y": -24,
            "acceleration_z": 1004,
            "tx_power": 4,
            "battery": 3027,
            "movement_counter": 43,
            "measurement_sequence_number": 26017,
            "mac": mac,
            "sequence": 1,
        }

        # Notify observer
        if self._handle_sensor_data is not None:
            self._handle_sensor_data(mac, data)
            self._logger.debug(f"Dummy data generated for {mac}")

    def _random_temp(self, mac):
        """
        Generate a random temperature in C
        :return:
        """
        # r is 0 <= r < 0.5 C
        r = random.random() * 0.5
        # Choose a sign for the change
        if random.random() > 0.5:
            r = r * -1.0
        self._sensor_data_control[mac]["temp"] = self._sensor_data_control[mac]["temp"] + r
        return self._sensor_data_control[mac]["temp"]

    def _random_humid(self, mac):
        """
        Generate a random humidity
        :return:
        """
        # r is 0 <= r < 1.0
        r = random.random()
        # Choose a sign for the change
        if random.random() >= 0.5:
            sign = 1.0
        else:
            sign = -1.0
        self._sensor_data_control[mac]["humid"] = self._sensor_data_control[mac]["humid"] + (r * sign)
        if self._sensor_data_control[mac]["humid"] > 100.0:
            self._sensor_data_control[mac]["humid"] = 100.0
        return self._sensor_data_control[mac]["humid"]

    def _random_timestamp(self):
        """
        Generate a random timestamp 0-5 seconds old
        :return: Generated timestamp
        """
        r = random.random() * 5.0
        if r > 4.5:
            r = 5.0
        now = datetime.now() - timedelta(seconds=r)
        return now

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
        self._logger.info("Waiting for DummySensorAdapter to terminate")
        self.join()
        self._logger.info("DummySensorAdapter terminated")

    def run(self):
        """
        Run random sensor data generation
        @return: None
        """
        # Create list of sensors to be emulated
        for mac, kvn in self._config[Configuration.CFG_RUUVITAGS].items():
            self._sensor_list.append(mac)
            tr = random.random() * 30.0  # 30C = 86F
            hr = random.random() * 80.0  # %
            self._sensor_data_control[mac] = {"temp": tr, "humid": hr}

        # Every time around update one randomly chosen sensor
        while not self._terminate:
            sensor = random.randint(0, len(self._sensor_list) - 1)
            mac = self._sensor_list[sensor]
            self._generate_ruuvi_data(mac)
            sleep(0.5)

    def terminate(self):
        """
        Terminate sensor data collection
        Returns: None
        """
        self._terminate = True
