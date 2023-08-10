#
# custom_widgets.py - composite tk widgets
# Copyright © 2023 Dave Hocker (email: AtHomeX10@gmail.com)
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


from tkinter import Label, Entry, Checkbutton, IntVar, StringVar
from tkinter.ttk import Combobox


class LabeledCheckboxWidget:
    """
    A compound label + checkbox widget
    """
    def __init__(self, parent, label="", value=None, row=0, column=0):
        """
        A checkbox with leading label
        :param parent:
        :param label:
        :param value: The string "true or "false"
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = IntVar()
        self._var.set(value == "true")
        self._control = Checkbutton(parent, text="", variable=self._var, width=6, bd=2)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the check value as the string true or false
        :return:
        """
        v = self._var.get()
        if v:
            return "true"
        return "false"

    def focus(self):
        """
        Set the focus on this control. Used to handle input errors.
        :return:
        """
        self._control.focus()


class LabeledStringWidget:
    """
    A compound label + string entry widget
    """
    def __init__(self, parent, label="", value="", row=0, column=0):
        """
        An integer input widget with leading label
        :param parent:
        :param label:
        :param value: A string value
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = StringVar()
        self._var.set(value)
        self._control = Entry(parent, textvariable=self._var, width=len(value)+1, bd=2)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the integer value as the string true or false
        :return:
        """
        v = self._var.get()
        return v

    def focus(self):
        """
        Set the focus on this widget. Used for error handling.
        :return:
        """
        self._control.focus()


class LabeledIntWidget:
    """
    A compound label + numeric entry widget
    """
    def __init__(self, parent, label="", value=0, row=0, column=0):
        """
        An integer input widget with leading label
        :param parent:
        :param label:
        :param value: An integer value
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = IntVar()
        self._var.set(int(value))
        self._control = Entry(parent, textvariable=self._var, width=5, bd=2)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the integer value as the string true or false
        :return:
        """
        v = self._var.get()
        try:
            v = int(v)
        except ValueError as ex:
            raise ex
        return v

    def focus(self):
        """
        Set the focus on this widget. Used for error handling.
        :return:
        """
        self._control.focus()


class LabeledFloatWidget:
    """
    A compound label + numeric entry widget
    """
    def __init__(self, parent, label="", value=0.0, row=0, column=0):
        """

        :param parent:
        :param label:
        :param value: A decimal/float value
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = StringVar()
        self._var.set(str(value))
        self._control = Entry(parent, textvariable=self._var, width=5, bd=2)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the integer value as the string true or false
        :return:
        """
        v = self._var.get()
        try:
            v = float(v)
        except ValueError as ex:
            raise ex
        return v

    def focus(self):
        """
        Set the focus on this widget. Used for error handling.
        :return:
        """
        self._control.focus()


class LabeledComboboxWidget:
    """
    A compound label + combobox widget
    """
    def __init__(self, parent, label="", value="", value_list=[], row=0, column=0, width=6):
        """

        :param parent:
        :param label:
        :param values:
        :param row:
        :param column:
        :return:
        """
        self._lbl = Label(parent, text=label)
        self._lbl.grid(row=row, column=column, padx=3, sticky="e")
        self._var = StringVar()
        self._var.set(value)
        self._control = Combobox(parent, textvariable=self._var, values=value_list, width=width)
        self._control.grid(row=row, column=column+1, padx=3, pady=3, sticky="w")

    def get(self):
        """
        Returns the check value as the string true or false
        :return:
        """
        v = self._var.get()
        return v

    def focus(self):
        self._control.focus()
