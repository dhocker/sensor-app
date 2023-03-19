#
# modal_dialog.py - A customized Dialog for use cases like an "about" dialog
# © 2023 Dave Hocker
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE file for more details.
#


from tkinter.simpledialog import Dialog
import tkinter
from tkinter import Text, Scrollbar, Button, Frame
from tkinter import font as tkfont


class ModalDialog(Dialog):
    def __init__(self, parent, title="Modal Dialog", heading=None, text=""):
        """
        Constructor for cutomized about dialog
        :param parent: The parent of the dialog, usually the top/root window
        :param title: Dialog box title
        :param heading: First line of the about text
        :param text: The about text (the main part of the dialog)
        """
        # Window height in lines
        self._max_window_height = 0
        # Window width in px
        self._max_window_width = 0

        self._text = text
        self._heading = heading

        # Must be last, calls body() method
        super().__init__(parent, title=title)

    def body(self, master) -> None:
        """
        Overrides base class definition of dialog box body
        :param master: Parent window
        :return: None
        """
        self._create_message_text(self._heading, self._text)

    def _create_message_text(self, heading, text, font="TkDefaultFont"):
        """
        Create the widgets containing the message box text.
        This code is isolated to facilitate grid positioning
        based on message box orientation.
        :param heading: First line in message box. It will appear in bold.
        :param text: Body of message text.
        :param font: Font name to be used. See https://tkdocs.com/tutorial/fonts.html.
        :return:
        """
        longest_line = ""
        text_lines = []

        # Find the longest line
        if text:
            text_lines = text.splitlines()
            for line in text_lines:
                if len(line) > len(longest_line):
                    longest_line = line

        # Use font to determine needed height
        f = tkfont.Font(self, font=font)

        metrics = f.metrics()
        self._line_height = metrics["linespace"] + 1
        padx = 25
        pady = self._line_height
        # Most of these numbers were determined empirically
        # The width is the longest line w/line-end plus 15% + padding
        self._char_width = int(float(f.measure(longest_line) + f.measure("\n")) * 1.15) + int(padx * 2)
        self._max_window_width += self._char_width
        # The height is set at a max of 40 lines with 2 lines for padding
        max_text_height = len(text_lines) + 2
        # The window height includes the button, logo image and more padding
        self._max_window_height += max_text_height + int((pady * 5) / self._line_height)

        # widgets

        self._frame = Frame(self, width=int(self._char_width / f.measure("M")), height=max_text_height,
                            bd=0, relief=tkinter.GROOVE)
        self._frame.pack()

        # The background color should be the same as the window/frame background.
        self._text_widget = Text(self._frame,
                                 width=int(self._char_width / f.measure("N")),
                                 height=max_text_height,
                                 bg=self.cget('bg'),  # use the window background
                                 bd=0,
                                 font=f)
        self._text_widget.pack(padx=padx, pady=pady)

        # If there is a heading, display it in bold
        if heading:
            self._text_widget.insert(tkinter.END, heading + "\n")
            self._text_widget.tag_add("heading", 1.0, 2.0)
            bold_font = tkfont.Font(self, family=font, size=14, weight="bold")
            self._text_widget.tag_config("heading", font=bold_font)

        # Insert the text body
        self._text_widget.insert(tkinter.END, text)
        # Make the text widget read-only
        self._text_widget.config(state=tkinter.DISABLED)

    def buttonbox(self):
        """
        Overrides base class definition of dialog buttons
        :return: None
        """

        box = Frame(self)

        w = Button(box, text="OK", width=10, command=self.ok)
        w.pack(side=tkinter.BOTTOM, padx=5, pady=5)

        self.bind("<Return>", self.ok)
        self.bind("<Escape>", self.cancel)

        box.pack()
