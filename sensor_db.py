#
# sensor_db.py - Sensor database
# Copyright © 2023 Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


import os
import datetime
from configuration import Configuration
import logging
import sqlite3


class SensorDB:
    """
    Sensor model (database)
    """
    def __init__(self):
        """
        Construct a sensor model instance
        """
        self._config = Configuration.get_configuration()
        self._logger = logging.getLogger("sensor_app")
        self._db = self._config[Configuration.CFG_SENSOR_DATABASE]
        self._init_db()

    def _init_db(self):
        """
        Initialize the sensor DB. If it doesn't exist, create it.
        :return: None
        """
        if os.path.isfile(self._db):
            # Database exists
            self._logger.info("Using database file: %s", self._db)
        else:
            # Database needs to be created
            self._create_database()
            self._logger.info("Created database file: %s", self._db)

        # Seed Sensors table with all known sensors
        self._seed_sensors()

        # Trim aged data records
        self.trim_sensor_data()

    def _create_database(self):
        """
        Create a new sensor DB
        :return: None
        """
        conn = self._get_connection()

        # All sensors
        conn.execute(
            "CREATE TABLE Sensors ( \
            id	integer, \
            mac text, \
            name text, \
            PRIMARY KEY(id), \
            UNIQUE (mac) ) \
            "
        )
        conn.commit()

        # Sensor data table
        conn.execute(
            "CREATE TABLE SensorData ( \
            id integer, \
            sensor_id integer, \
            format integer, \
            temperature	real, \
            humidity real, \
            pressure real, \
            tx_power integer, \
            battery integer, \
            data_time timestamp, \
            PRIMARY KEY(id), \
            FOREIGN KEY (sensor_id) REFERENCES Sensors(id) ) \
            "
        )
        conn.commit()

        conn.close()

    def _seed_sensors(self):
        """
        Seed the sensor table with sensors defined in the config file
        :return: None
        """
        for mac in self._config[Configuration.CFG_RUUVITAGS].keys():
            sensor_id = self._get_sensor_id(mac)
            name = self._config[Configuration.CFG_RUUVITAGS][mac]["name"]
            if sensor_id is None:
                self.add_sensor(mac, name)
                self._logger.info("Added sensor to Sensors: %s", mac)
            else:
                # Update the sensor's name. DO NOT delete the record id.
                self.update_sensor_name(sensor_id, name)
                self._logger.info("Updated existing sensor: %s %s", mac, name)

    def update_sensor_name(self, sensor_id, name):
        """
        Update the sensor name for an existing sensor
        :param sensor_id: The id of the sensor to be updated
        :param name: The new sensor name
        :return: NOne
        """
        conn = None
        try:
            conn = self._get_connection()
            c = self._get_cursor(conn)
            c.execute(
                "UPDATE Sensors SET name=? WHERE id=?", (name, sensor_id, )
            )
            conn.commit()

            # Get id of inserted record
            id = c.lastrowid
        except Exception as ex:
            # Should fail on duplicate mac
            self._logger.error(str(ex))
            id = None
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

    def add_sensor(self, mac, name):
        """
        Add a sensor to the Sensors table
        :param mac: The sensor's mac
        :param name: The sensor's name (maybe from the config file)
        :return: The record id of the inserted record
        """
        # If the mac is already registered update the name and return the id
        id = self._get_sensor_id(mac)
        if id is not None:
            self.update_sensor_name(id, name)
            return id

        # Since this mac has not been registered, add it to the table
        conn = None
        try:
            conn = self._get_connection()
            c = self._get_cursor(conn)
            c.execute(
                "INSERT INTO Sensors (mac,name) values (?, ?)", (mac, name, )
            )
            conn.commit()

            # Get id of inserted record
            id = c.lastrowid
        except Exception as ex:
            # Should fail on duplicate mac
            self._logger.error(str(ex))
            id = None
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

        return id

    def add_sensor_data(self, mac, data):
        """
        Add a sensor data record to the SensorData table
        :param mac: The sensor's mac in the form E0:D0:98:47:DD:CC
        :param data: Dict of key/value pairs (the sensor data)
        :return: Returns the record id
        """
        conn = None
        # TODO Handle unregistered sensor with no entry in the config file
        try:
            conn = self._get_connection()
            c = self._get_cursor(conn)
            c.execute(
                "INSERT INTO SensorData ("
                "sensor_id,format,temperature,humidity,pressure,tx_power,battery,data_time)"
                "values ((SELECT id FROM Sensors WHERE mac=? LIMIT 1), ?, ?, ?, ?, ?, ?, ?) ",
                (
                    mac, data["data_format"], data["temperature"], data["humidity"],
                    data["pressure"], data["tx_power"], data["battery"],
                    data["timestamp"],
                )
            )
            conn.commit()

            # Get id of inserted record
            id = c.lastrowid
        except Exception as ex:
            self._logger.error(str(ex))
            id = None
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

        return id

    def reset_sensor_data(self):
        """
        Delete all sensor data records
        :return: None
        """
        conn = self._get_connection()
        c = self._get_cursor(conn)
        c.execute("DELETE FROM SensorData")
        conn.commit()
        conn.close()

    def trim_sensor_data(self, time_period_hours=24):
        """
        Trim old sensor data records. Typically, only 24 hours of data is kept.
        :param time_period_hours: All records older than this value are deleted
        :return: None
        """
        trim_time = datetime.datetime.now() - datetime.timedelta(hours=time_period_hours)
        conn = self._get_connection()
        c = self._get_cursor(conn)
        start = datetime.datetime.now()
        c.execute("DELETE FROM SensorData where data_time<?", (str(trim_time),))
        conn.commit()
        elapsed = datetime.datetime.now() - start
        # It's not clear how long this will take on a RaspberryPi 3 or 4.
        # It is expected that the database will get as large as 40-50 MB.
        self._logger.info(f"Sensor data trimmed in {elapsed.total_seconds():f} sec")

        rset = c.execute("SELECT COUNT(*) as record_count FROM SensorData")
        result = rset.fetchone()["record_count"]
        self._logger.info(f"Sensor DB record count after trimming: {result}")

        conn.close()

    def _get_sensor_id(self, mac):
        """
        Return the Sensor id for a sensor identified by mac
        :param mac: The sensor's mac
        :return: The sendor id of the sensor (in the Sensors table)
        """
        conn = None
        result = None
        try:
            conn = self._get_connection()
            c = self._get_cursor(conn)
            rset = c.execute(
                "SELECT id FROM Sensors WHERE mac=:mac",
                {"mac": mac}
            )
            result = rset.fetchone()["id"]
        except Exception as ex:
            pass
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

        return result

    def _get_connection(self):
        """
        Return a database connection instance
        :return: A Connection instance
        """
        # TODO Can the connection be kept open to avoid this overhead on ever operation?
        # In the current design, a connection is opened and closed for each DB operation.
        # This may be effective enough. But, it may not.
        conn = sqlite3.connect(self._db)
        # We use the row factory to get named row columns. Makes handling row sets easier.
        conn.row_factory = sqlite3.Row
        # The default string type is unicode. This changes it to UTF-8.
        conn.text_factory = str
        # Enable foreign keys for this connections
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()
        return conn

    def _get_cursor(self, conn):
        """
        Return a cursor instance on a given database connection
        :param conn: A Connection instance
        :return: A Cursor instance on the connection
        """
        return conn.cursor()
