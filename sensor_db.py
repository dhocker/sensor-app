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
        self._database_timeout = self._config[Configuration.CFG_DATABASE_TIMEOUT]
        self._logger.debug(f"Database timout value: {self._database_timeout:f}")
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
            CONSTRAINT fk_sensors \
                FOREIGN KEY (sensor_id) REFERENCES Sensors(id) ON DELETE CASCADE \
            )"
        )
        conn.commit()

        conn.close()

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

    def add_sensor(self, mac):
        """
        Add a sensor to the Sensors table
        :param mac: The sensor's mac
        :return: The inserted record
        """
        # Try to use config file to determine sensor name
        if mac in self._config[Configuration.CFG_RUUVITAGS]:
            name = self._config[Configuration.CFG_RUUVITAGS][mac]["name"]
        else:
            name = "N/A"

        # If the mac is already registered update the name and return the id
        sensor_rec = self._get_sensor_record(mac)
        if sensor_rec is not None:
            # If the current sensor record name does not match the config, update it
            if sensor_rec["name"] != name:
                if mac in self._config[Configuration.CFG_RUUVITAGS]:
                    self.update_sensor_name(sensor_rec["id"], name)
                    self._logger.info(f"Updated sensor id {sensor_rec['id']} from {sensor_rec['name']} to {name}")
                    sensor_rec = self._get_sensor_record(mac)
            return sensor_rec

        # Since this mac has not been registered, add it to the table
        # Prefer to use the DB, then the config file, for the sensor's name
        conn = None
        try:
            conn = self._get_connection()
            c = self._get_cursor(conn)
            c.execute(
                "INSERT INTO Sensors (mac,name) values (?, ?)", (mac, name, )
            )
            conn.commit()

            # Return inserted record
            sensor_rec = {
                "id": c.lastrowid,
                "mac": mac,
                "name": name
            }
        except Exception as ex:
            # Should fail on duplicate mac
            self._logger.error(str(ex))
            sensor_rec = None
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

        return sensor_rec

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

    def _get_sensor_record(self, mac):
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
                "SELECT id, mac, name FROM Sensors WHERE mac=:mac",
                {"mac": mac}
            )
            result = rset.fetchone()
        except Exception as ex:
            pass
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

        return result

    def get_all_sensor_records(self):
        """
        Return all sensor records
        :return: A list of sensor table records
        """
        conn = None
        result = None
        try:
            conn = self._get_connection()
            c = self._get_cursor(conn)
            rset = c.execute(
                "SELECT * FROM Sensors"
            )
            result = SensorDB._rows_to_dict_list(rset)
        except Exception as ex:
            pass
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

        return result

    def delete_sensor_record(self, id):
        """
        Delete a sensor table record
        :@param Record id to be deleted
        :return: A list of sensor table records
        """
        conn = None

        # Note that because of foreign key constraints all sensor data
        # records must be deleted before the sensor record can be deleted
        try:
            conn = self._get_connection()
            c = self._get_cursor(conn)
            c.execute(
                "DELETE FROM Sensors WHERE id=:id",
                {"id": id}
            )
            conn.commit()
        except Exception as ex:
            self._logger.error(f"Exception while deleting sensor ID {id}")
            self._logger.error(str(ex))
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

    def update_sensor_record(self, id, name):
        """
        Delete a sensor table record
        :@param id: ID of record to be updated
        :@param name: New sensor name
        :return: None
        """
        conn = None

        try:
            conn = self._get_connection()
            c = self._get_cursor(conn)
            c.execute(
                "UPDATE Sensors SET name=:name WHERE id=:id",
                {"name": name, "id": id}
            )
            conn.commit()
        except Exception as ex:
            self._logger.error(f"Exception while updating sensor ID {id}")
            self._logger.error(str(ex))
        finally:
            # Make sure connection is closed
            if conn is not None:
                conn.close()

    def get_sensor_history(self, mac, progress_dlg=None):
        """
        Fetch all of the interesting sensor history
        @param mac: The sensor of interest
        @param progress_dlg: Optional progress dialog for reporting query progress
        @return: A list of dicts where each list item is a DB record
        """
        # Find the sensor record for this sensor
        sensor_rec = self._get_sensor_record(mac)

        conn = None
        result = None
        try:
            if progress_dlg is not None:
                progress_dlg.Pulse(f"Querying history for {mac}")
            conn = self._get_connection()
            c = self._get_cursor(conn)
            rset = c.execute(
                "SELECT temperature, humidity, data_time FROM SensorData WHERE sensor_id=:id",
                {"id": sensor_rec["id"]}
            )
            if progress_dlg is not None:
                progress_dlg.Pulse(f"Converting result rows to dictionary {mac}")
            result = SensorDB._rows_to_dict_list(rset)
            # Convert data_time from str to a datetime
            row_counter = 0
            for r in result:
                if row_counter % 100 == 0:
                    if progress_dlg is not None:
                        progress_dlg.Pulse(f"Processing record {row_counter} of {len(result)}")
                # Cover case when timestamp has no fraction of a second
                if "." in r["data_time"]:
                    r["data_time"] = datetime.datetime.strptime(r["data_time"], "%Y-%m-%d %H:%M:%S.%f")
                else:
                    r["data_time"] = datetime.datetime.strptime(r["data_time"], "%Y-%m-%d %H:%M:%S")
                row_counter += 1
        except Exception as ex:
            self._logger.error(f"Exception querying sensor history for {mac}")
            self._logger.error(str(ex))
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
        # TODO Make timeout value a config setting
        conn = sqlite3.connect(self._db, timeout=self._database_timeout)
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

    @classmethod
    def _rows_to_dict_list(cls, rows):
        """
        Convert a list of SQLite rows to a list of dicts
        :param rows: SQLite row set to be converted
        :return:
        """
        dl = []
        for row in rows.fetchall():
            dl.append(cls._row_to_dict(row))
        return dl

    @classmethod
    def _row_to_dict(cls, row):
        """
        Convert an SQLite row set to a dict
        :param row: the row set to be converted
        :return: a dict containing all of the columns in the row set
        """
        d = {}
        for key in row.keys():
            d[key] = row[key]
        return d

    @property
    def _date_time_format(self):
        """
        Format of datetime stored as a timestamp
        @return: Format string
        """
        return "%Y-%m-%d %H:%M:%S.%f"
