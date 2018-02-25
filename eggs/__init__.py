# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
# Copyright (C) 2016 - 2018 Mod Organizer contributors.
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
import urllib2

import pip


def download(url, filename):
    if os.path.exists(filename):
        return False

    data = urllib2.urlopen(url)
    with open(filename, 'wb') as outfile:
        while True:
            block = data.read(4096)
            if not block:
                break
            outfile.write(block)
    return True


path = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))

for dep in [
    "https://gitlab.com/LePresidente/python-build-tools/uploads/18a195f7945ca35ad563b428739f254b/buildtools-0.0.2-py2.7.egg"]:
    eggpath = os.path.join(path, os.path.basename(dep))
    download(dep, eggpath)
    sys.path.append(eggpath)

for dep in ["decorator", "lxml", "PyYAML", "six", "jinja2", "psutil", "patch", "networkx", "pydot", "pydotplus"]:
    destpath = "{0}/{1}".format(path, dep)
    if not os.path.exists(destpath):
        pip.main(["install", "--target={0}".format(destpath), dep])
    sys.path.append(destpath)

""" neither of these work. particularly building pygraphviz requires a specific VC version in a specific location


for dep in ["pygraphviz"]:
    pip.main(["install", "--install-option=\"--prefix={}\"".format(path), dep])


for dep in ["https://pypi.python.org/packages/source/p/pygraphviz/pygraphviz-1.3.1.tar.gz"]:
    basename = os.path.basename(dep)
    libpath = os.path.join(path, basename)
    if download(dep, libpath):
        with tarfile.open(libpath, 'r') as tar:
            tar.extractall(path=path)
        cwd = os.path.join(path, os.path.splitext(os.path.splitext(basename)[0])[0])
        call(["python", "setup.py", "install"], cwd=cwd)
"""
