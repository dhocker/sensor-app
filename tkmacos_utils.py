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
# Adapted from code in the following article:
#   https://stackoverflow.com/questions/30009909/change-title-of-tkinter-application-in-os-x-menu-bar
#

def set_menubar_app_name(app_name):
    """
    Fix macos menu bar so the app name appears instead of Python. This function
    MUST be called before starting tkinter (by creating a TK() instance).
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
