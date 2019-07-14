# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2019 Mod Organizer contributors.
#
# This file is part of Mod Organizer.
#
# Mod Organizer is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Mod Organizer is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Mod Organizer.  If not, see <http://www.gnu.org/licenses/>.
import os.path
import sys
import urllib.request, urllib.error, urllib.parse
import subprocess


def download(url, filename):
    if os.path.exists(filename):
        return False

    data = urllib.request.urlopen(url)
    with open(filename, 'wb') as outfile:
        while True:
            block = data.read(4096)
            if not block:
                break
            outfile.write(block)
    return True


path = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))

for dep in [
    "https://gitlab.com/LePresidente/python-build-tools/uploads/2d5288682a4905940c8d37422d4128f0/pybuildtools-0.2.1-py3.7.egg"]:
    eggpath = os.path.join(path, os.path.basename(dep))
    download(dep, eggpath)
    sys.path.append(eggpath)

for dep in ["decorator", "lxml", "PyYAML", "six", "jinja2", "psutil", "patch", "networkx", "pydot", "pydotplus","colorama","tqdm"]:
    destpath = "{0}/{1}".format(path, dep)
    if not os.path.exists(destpath):
        subprocess.check_call(["python", "-m", "pip", "install", "--target={0}".format(destpath), dep])
    sys.path.append(destpath)
