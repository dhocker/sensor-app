# -*- coding: UTF-8 -*-
#
# Display controller
# Copyright © 2023  Dave Hocker (email: athomex10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the LICENSE.md file for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (the LICENSE.md file).  If not, see <http://www.gnu.org/licenses/>.
#
# How to turn official 7" touchscreen display on and off
# https://scribles.net/controlling-display-backlight-on-raspberry-pi/
#
# OFF
# echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power
# ON
# echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power
#
# And, how to do it for an HDMI attached display.
#
# OFF
# vcgencmd display_power 0
# ON
# vcgencmd display_power 1
#

import subprocess
import platform
import logging

try:
    # Only on a real RPi
    import rpi_backlight
except:
    pass


class DisplayController:
    """
    The display is controlled by a state machine.
    Display off
    Display on
    Count down to display off
    Count down to display on
    Unknown

    """

    def __init__(self, count_down_time=600, brightness=30):
        """
        Class constructor
        :param count_down_time: in seconds, how long to wait before entering the
            display off state.
        :param brightness: 0-100 where 0 is off
        """
        # Create a logger
        self._logger = logging.getLogger("sensor_app")

        # states
        self._state_unknown = 0
        self._state_display_off = 1
        self._state_display_on = 2
        self._display_states = ["unknown", "off", "on"]
        self._count_down_time = count_down_time
        self._count_down = count_down_time
        # 0=off, 1=on
        self._backlight_state = 0
        # An instance of the backlight class
        self._backlight = None

        # By definition the display is on when the app starts
        self._display_state = self._state_display_on

        # This path needs to be determined based on machine/OS version
        # This value works for RPi OS Desktop 64-bit aarch64.
        # It will not work for 32-bit OSes.
        if self._backlight is None:
            backlight_path = self.get_backlight_path()
            self._logger.debug(f"Backlight path: {backlight_path}")
            if backlight_path is None:
                self._backlight = None
            elif backlight_path != "":
                self._backlight = rpi_backlight.Backlight(backlight_path)
            elif backlight_path == "":
                self._backlight = rpi_backlight.Backlight()
            else:
                self._logger.error("Could not resolve location of backlight")

        self.set_display_backlight_brightness(brightness)

    def reset_count_down(self):
        """
        Reset the countdown timer
        :return:
        """
        self._logger.debug("Reset count down time")
        self._count_down = self._count_down_time
        self._set_display_state(1)

    def count_down(self, tsec):
        """
        Count down to display off
        :param tsec: Amount of time in seconds to count off
        :return:
        """
        self._logger.debug(f"Count down: {self._count_down}")
        if self._display_state == self._state_display_on:
            self._count_down -= tsec
            if self._count_down <= 0:
                # turn off display/backlight
                self._set_display_state(0)

    """
    The techniques used to manage different displays was
    found at: https://scribles.net/controlling-display-backlight-on-raspberry-pi/
    """
    
    def _set_display_state(self, new_state):
        """
        Display management state machine
        :param new_state: The desired new state where 0=off and 1=on
        :return: None
        """
        if self._display_state == self._state_display_off:
            # Current state is display off
            if new_state:
                # New state is on
                self._display_state = self._state_display_on
                self.display_on()
            else:
                pass
        elif self._display_state == self._state_display_on:
            # Current state is display on
            if not new_state:
                # New state is off
                self._display_state = self._state_display_off
                self.display_off()
            else:
                pass
        else:
            # Unknown state
            self._logger.debug("Undefined state %s", self._display_state)

    def get_display_state(self):
        """
        Returns the human-readable state
        :return: "unknown", "off" or "on"
        """
        return self._display_states[self._display_state]

    @staticmethod
    def is_hdmi_display():
        """
        Answers the question: Is the current display HDMI?
        Otherwise, it is assumed to be the RPi 7" touchscreen.
        """
        try:
            res = subprocess.run(["tvservice", "-s"], stdout=subprocess.PIPE)
            res = str(res.stdout, 'utf-8')
            if res.find("HDMI") != -1:
                return True
            return False
        except:
            pass
        return False

    @staticmethod
    def is_raspberry_pi():
        # A weak test for the RPi
        return platform.machine() in ["armv7l", "armv8l", "aarch64"]

    @staticmethod
    def get_backlight_path():
        """
        Return the path to the backlight for this machine. This method was
        necessitated by RPi OS 64-bit which changed the path to the backlight.
        :return:
        """
        if DisplayController.is_raspberry_pi():
            if platform.machine() in ["aarch64"]:
                return "/sys/class/backlight/10-0045"
            return ""
        return None

    """
    These methods can be overriden in a derived class
    to provide advanced customization of each state.
    Each method is called when the state is entered.
    """

    def display_on(self):
        self.turn_display_on()

    def display_off(self):
        self.turn_display_off()

    """
    The techniques used to manage diffrent displays was
    found at: https://scribles.net/controlling-display-backlight-on-raspberry-pi/
    Note that these are class methods because there is only one physical display.
    """

    @classmethod
    def query_display_state(self):
        state = self._state_unknown
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                # subprocess.run(["vcgencmd", "display_power", "1"])
                state = self._state_unknown
            else:
                # rpi 7" touchscreen
                if self._backlight.power:
                    state = self._state_display_on
                else:
                    state = self._state_display_off
        else:
            pass
        self._logger.debug("Current display state %s", self._display_states[state])
        return state

    def turn_display_on(self):
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                subprocess.run(["vcgencmd", "display_power", "1"])
            else:
                # rpi 7" touchscreen
                # a = "echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power"
                self._logger.debug("Turning display power on")
                # subprocess.check_output(a, shell=True)
                self._backlight.power = True
        else:
            pass
        self._backlight_state = 1
        self._logger.debug("Display turned on")

    def turn_display_off(self):
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                subprocess.run(["vcgencmd", "display_power", "0"])
            elif DisplayController.is_raspberry_pi():
                # rpi 7" touchscreen
                # a = "echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power"
                self._logger.debug("Turning display power off")
                # subprocess.check_output(a, shell=True)
                self._backlight.power = False
        else:
            pass
        self._backlight_state = 0
        self._logger.debug("Display turned off")

    def set_display_backlight_brightness(self, brightness):
        if DisplayController.is_raspberry_pi():
            if DisplayController.is_hdmi_display():
                pass
            elif DisplayController.is_raspberry_pi():
                # rpi 7" touchscreen
                self._logger.debug("Setting display brightness")
                rpi_backlight.Backlight.brightness = brightness
        else:
            pass

        self._brightness = int(brightness)
        self._logger.debug("Display backlight brightness set")
