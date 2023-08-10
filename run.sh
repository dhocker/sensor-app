#!/bin/bash
echo Start sensor-app
cd /home/pi/rpi/wx-sensor-app
# Put the venv at the front of the path
# When its python is run, it will activate the venv
PATH=~/Virtualenvs/sensor-app3/bin:$PATH
python wx_sensor_app.py
