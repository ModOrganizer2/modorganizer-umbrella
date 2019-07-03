# Copyright (c) 2019 Riverbank Computing Limited <info@riverbankcomputing.com>
#
# This file is part of PyQt5.
#
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
#
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
#
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.

# flake8: noqa

from ctypes import CDLL


def find_qt():
    import os

    try:
        qt5 = CDLL("Qt5Core")
    except OSError as e:
        path = os.environ['PATH']

        dll_dir = os.path.dirname(__file__) + '\\Qt\\bin'
        if os.path.isfile(dll_dir + '\\Qt5Core.dll'):
            path = dll_dir + ';' + path
            os.environ['PATH'] = path
        else:
            for dll_dir in path.split(';'):
                if os.path.isfile(dll_dir + '\\Qt5Core.dll'):
                    break
            else:
                raise ImportError("unable to find Qt5Core.dll on PATH")

        try:
            os.add_dll_directory(dll_dir)
        except AttributeError:
            pass


find_qt()
del find_qt
