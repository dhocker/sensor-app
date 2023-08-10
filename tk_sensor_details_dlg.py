# coding: utf-8
#
# SensorDetailsDlg class implementation
# Copyright © 2022 Dave Hocker (email: AtHomeX10@gmail.com)
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


from tkinter import Tk, Frame, Button, Label, simpledialog


class SensorDetailsDlg(simpledialog.Dialog):
    """
    Reference: https://docs.python.org/3/library/dialog.html#module-tkinter.simpledialog
    """
    def __init__(self, parent, name, sensor_data):
        """
        Create a sensor details dialog box
        :param parent: Parent of this dialog
        :param name: Sensor name
        :param sensor_data: dict of sensor data keys/values.
        """
        self._name = name
        self._sensor_data = sensor_data
        self._fr = None
        self._gr = 0

        # Note that the base class constructor calls the body method
        super(SensorDetailsDlg, self).__init__(parent, title=f"Sensor Details for {name}")

    def body(self, parent):
        """
        Provides the main content of the dialog. In this case all the sensor data.
        :param parent: The dialog's content frame.
        :return:
        """
        # self._fr = Frame(parent)
        self._fr = parent
        self._fr.pack()

        lbl = Label(self._fr, text="Sensor values")
        lbl.grid(row=self._gr, column=0, sticky="W")
        self._gr += 1

        # Display keys in sort order
        for key in sorted(self._sensor_data.keys()):
            lbl = Label(self._fr, text=key)
            lbl.grid(row=self._gr, column=0, sticky="W")
            lbl = Label(self._fr, text=self._sensor_data[key])
            lbl.grid(row=self._gr, column=1, sticky="W")
            self._gr += 1

    def buttonbox(self) -> None:
        """
        Our dialog only needs an OK button. Note that it invokes
        the Dialog class ok method (which calls the apply method).
        :return:
        """
        btn = Button(self._fr, text="OK", width=6, command=self.ok)
        btn.grid(row=self._gr, column=0, columnspan=2, pady=20)
        # Close dialog on enter/return or esc
        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.ok)

    def apply(self):
        """
        Called when OK button is clicked
        :return:
        """
        pass
