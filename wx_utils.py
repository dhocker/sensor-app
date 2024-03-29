#
# wx_utils.py - utility functions for wx components
# Copyright © 2023 by Dave Hocker (AtHomeX10@gmail.com)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# See the LICENSE.md file for more details.
#


import os
import wx


def load_bitmap(bitmap_name):
    """
    Load a bitmap file. When running under macOX bitmaps are in the
    images folder. Under the IDE images are in the resources folder.
    :param bitmap_name: Name of bitmap file to load.
    :return: Returns a Bitmap instance
    """
    # Debugging code
    # if not self._once:
    #     self._once = True
    #     dlg = wx.MessageDialog(self, os.getcwd(), "Where are we?", wx.OK | wx.ICON_INFORMATION)
    #     dlg.ShowModal()

    bitmap_file = os.path.join("images", bitmap_name)
    if os.path.exists(bitmap_file):
        return wx.Bitmap(bitmap_file)
    return wx.Bitmap(os.path.join("resources", bitmap_name))


def show_error_message(parent, message, title):
    """
    Show a modal error message dialog box
    :param parent: Parent window/frame or None
    :param message: Error message text
    :param title: Dialog title
    :return: None
    """
    dlg = wx.MessageDialog(parent,
                           message,
                           title,
                           wx.OK | wx.ICON_ERROR)
    dlg.ShowModal()


def show_info_message(parent, message, title):
    """
    Show a modal information message dialog box
    :param parent: Parent window/frame or None
    :param message: Infomation message text
    :param title: Dialog title
    :return: None
    """
    dlg = wx.MessageDialog(parent,
                           message,
                           title,
                           wx.OK | wx.ICON_INFORMATION)
    dlg.ShowModal()


def set_menubar_app_name(app_name):
    """
    Fix macos menu bar so the app name appears instead of Python. This function
    MUST be called before starting wxPython.
    :param app_name: The name to be placed on the macos menubar.
    :return: None
    """
    # Check if we're on OS X, first.
    from sys import platform

    if platform == 'darwin':
        # This has to be done BEFORE firing up tkinter
        from Foundation import NSBundle

        bundle = NSBundle.mainBundle()
        if bundle:
            info = bundle.localizedInfoDictionary() or bundle.infoDictionary()
            if info and info['CFBundleName'] == 'Python':
                info['CFBundleName'] = app_name
                info["CFBundleExecutable"] = app_name
