#
# sensor_utils.py - utility functions
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

import datetime


def to_fahrenheit(centigrade):
    return 32.0 + (centigrade * 1.8)


def now_str():
    """
    Return a formatted string containing the current date and time
    :return:
    """
    now_dt = datetime.datetime.now()
    # custom format to remove unwanted leading zeros
    ampm = "am"
    if now_dt.hour >= 12:
        ampm = "pm"
    hour = now_dt.hour
    if hour > 12:
        hour -= 12
    return f"{now_dt.year:4d}-{now_dt.month:02d}-{now_dt.day:02d}  {hour:2d}:{now_dt.minute:02d} {ampm}"
