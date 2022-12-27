# Sensor App for RuuviTag Sensors

## Overview
This project is a Python based sensor app for monitoring RuuviTag sensors. It is all
written in Python 3. It uses TKinter to implement the GUI. It can run on most any system
that has support for BLE. It was developed mostly on a Raspberry Pi model 3 and 4 with the
7" Raspberry Pi touch screen.

## Hardware Requirements

* a [Raspberry Pi](https://en.wikipedia.org/wiki/Raspberry_Pi#Networking) model 3, model 4,
Zero W or Zero 2 W (one with WiFi and Bluetooth support)

# Installation and Setup

## Install RPi Prerequisites

Be sure to check out the 
[ruuvitag-sensor instructions](https://github.com/ttu/ruuvitag-sensor/blob/master/install_guide_pi.md) 
for installing on an RPi. There is a significant number of prerequisite parts to be installed
before you can receive data from a RuuviTag.

At a minimum you need to install the following.

```shell
sudo apt-get install bluetooth bluez blueman
sudo apt-get install bluez-hcidump
```
NOTE: On the latest versions of Raspberry Pi OS desktop, blueman does not seem to be required.

Reboot the RPi after installing the bluetooth packages.

## Download Files
The easiest way to get the project files is to clone the GitHub repository.

```shell
cd
mkdir rpi
cd rpi
git clone https://github.com/dhocker/sensor-app.git
```

The project assumes that its root is at ~/rpi/sensor-app.

## Create a VENV
Here, [virtualenv](https://virtualenv.pypa.io/en/latest/) and 
[virtualenvwrapper](https://virtualenvwrapper.readthedocs.io/en/latest/) are assumed.
If you install these tools it is recommended that you set up ~/Virtualenvs as
the folder for keeping VENVs. This will minimize the number of changes you will need
to make later.

```shell
mkvirtualenv -p python3 -r requirements.txt sensor-app3
```
## Create a Configuration File
sensor-app can be controlled through sensor_app.conf. Note that this file **is not**
part of the GitHub repo. However, there is a sensor_app.example.conf file that
serves as a template. The configuration file must be kept in the root directory of the project.

You can make changes to the configuration file by using the File|Settings menu item.

The configuration file is composed of JSON and looks like this.

```json
{
    "ruuvitags": {
        "XX:XX:XX:XX:XX:XX": {
            "name": "Kitchen"
        },
        "XX:XX:XX:XX:XX:XX": {
            "name": "Outdoor"
        }
    },
    "use_test_data": "true",
    "debug_sensors": "false",
    "log_level": "debug",
    "log_console": "true",
    "update_interval": 3.0,
    "temperature_format": "F",
    "sensors_per_row": 5,
    "offline_time": 600,
    "offline_color": "#ff3300",
    "low_battery_threshold": 1800,
    "low_battery_color": "#FFFF00",
    "normal_background_color": "#66ffff"
}
```

The most important use of the configuration file is to assign a human-readable name to a sensor.
Otherwise, your sensors will be shown with names derived from the last 4 digits of their mac.

| Key                     | Description                                                                                    |
|-------------------------|------------------------------------------------------------------------------------------------|
| ruuvitags               | Defines a human-readable name for a given tag's mac                                            |
| use_test_data           | When true, use test data (useful for macOS testing). When false, collect data from sensors     | 
| debug_sensors           | When true, dumps each sensor's data into a file.                                               |
| log_level               | debug, info, warning or error. Controls the verbosity of the log file.                         |
| log_console             | When true, logs to file and to the console.                                                    |
| update_interval         | Time between LCD updates expressed in seconds (as a float).                                    |
| temperature_format      | "F" for fahrenheit or "C" for centigrade.                                                      |
| sensors_per_row         | The maximum number of sensors in one row of the display                                        |
| offline_time            | If no data is received from a sensor in this time (seconds), the sensor is considered offline. |
| offline_color           | Color to mark sensor when it is detected as offline #rrggbb                                    |
| low_battery_threshold   | Battery value that triggers a low battery warning                                              |
| low_battery_color       | Color to mark sensor when a low battery condition is detected #rrggbb                          |
| normal_background_color | Default/normal color for a sensor #rrggbb                                                      |

All colors are expressed in the format #rrggbb where r, g and b are hex numbers (0-F). For example #00FF00 is green.
This is standard HTML color format.

### How to Find a RuuviTag's mac
There are several ways to find a tag's mac (it is not on the sensor).

The first way is to use the Ruuvi app on an iPad, iPhone or Android phone. Activate one sensor at a time
and check the app to see what mac shows up.

The second way is to turn on "debug_sensors" in the configuration file and look at the 
[ruuvi.json](#ruuvitag-data) file it produces. Again, activate one sensor at a time.

And, a third way is to look in the current log file. sensor_monitor will log a sensor
when it is first detected. Immediately after activating a sensor watch the current log file.
The taillog.sh script is provided to do just that.

```shell
./taillog.sh
```
Here's what you should see.
```
2022-10-24 10:58:47, MainThread, sensor_monitor, INFO, Monitoring sensor 11:11:11:11:12:34 1234
```
If the sensor is configured, its name will appear instead of 1234. If the sensor has not been
configured you can capture its mac (the 11:11:11:11:12:34 in the above log line) and add it to sensor_monitor.conf.

## Run from Command Line
If you prefer to run sensor-app from a terminal, use the following commands.
```shell
workon sensor-app3
python sensor_app.py
```

# Reference

## RuuviTag Data
[Format 5 Reference](https://github.com/ruuvi/ruuvi-sensor-protocols/blob/master/dataformat_05.md)

Example of data returned by the ruuvitag-sensor module.
```json
{
    "D5:95:F0:51:21:F2": {
        "data_format": 5,
        "humidity": 49.55,
        "temperature": 25.66,
        "pressure": 1010.37,
        "acceleration": 1006.8326573964514,
        "acceleration_x": -172,
        "acceleration_y": -8,
        "acceleration_z": 992,
        "tx_power": 4,
        "battery": 3002,
        "movement_counter": 54,
        "measurement_sequence_number": 34834,
        "mac": "d595f05121f2"
    },
    "D5:68:78:B9:E0:F1": {
        "data_format": 5,
        "humidity": 49.95,
        "temperature": 25.2,
        "pressure": 1009.88,
        "acceleration": 1020.5802271257268,
        "acceleration_x": 20,
        "acceleration_y": 28,
        "acceleration_z": 1020,
        "tx_power": 4,
        "battery": 3146,
        "movement_counter": 26,
        "measurement_sequence_number": 58144,
        "mac": "d56878b9e0f1"
    }
}
```
