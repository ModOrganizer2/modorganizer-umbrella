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
import sys
import os
import urllib.request
import json
import subprocess
import logging
from config import config
from unibuild.modules.git import Clone
from unibuild.modules.urldownload import URLDownload


def Popen(cmd, **kwargs):
    pc = ''
    if 'cwd' in kwargs:
        try:
            pc += os.path.relpath(kwargs['cwd'], os.path.abspath('..'))
        except ValueError:
            pc += kwargs['cwd']
    pc += '>'
    for arg in cmd:
        pc += ' ' + arg
    print(pc)
    return subprocess.Popen(cmd,**kwargs)


class Release(URLDownload):
    def __init__(self, author, project, version, filename, extension="zip", tree_depth=0):
        super(Release, self) \
            .__init__("https://github.com/{author}/{project}/releases/download/{version}/"
                      "{filename}.{extension}".format(author=author,
                                                      project=project,
                                                      version=version,
                                                      filename=filename,
                                                      extension=extension), tree_depth)
        self.set_destination("{}-{}".format(project, version))


class Tag(URLDownload):
    def __init__(self, author, project, tag, version, extension="zip", tree_depth=1):
        super(Tag, self).__init__("https://github.com/{author}/{project}/archive/{tag}.{extension}"
                                             .format(author=author,
                                                     project=project,
                                                     tag=tag,
                                                     extension=extension), tree_depth)
        self.set_destination("{}-{}".format(project, tag))


class Source(Clone):
    def __init__(self, author, project, branch="master", feature_branch=None, super_repository=None, update=True, commit=None, pr_label=None, shallowclone=False):
        self.__author = author
        self.__project = project
        if config['shallowclone']:
            self.shallowclone = True
        self.__pr_label = pr_label

        super(Source, self).__init__("https://github.com/{author}/{project}.git".format(author=author, project=project),
                                     branch, feature_branch, super_repository, update, commit, shallowclone)

        self.set_destination(project)

    def process(self, progress):
        result = super(Source, self).process(progress)
        if result is False:
            return False

        if self.__pr_label is not None:
            url = "https://api.github.com/repos/{}/{}/pulls".format(self.__author, self.__project)
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            filtered_data = [x for x in data if x["head"]["label"] == self.__pr_label]
            sys.stdout.write(filtered_data.__str__())
            if len(filtered_data) > 0:
                pr_number = filtered_data[0]["number"]
                proc = Popen([config['paths']['git'], "fetch", "-q", "origin", "+refs/pull/{}/merge:".format(pr_number)],
                             cwd=self._context["build_path"],
                             env=config["__environment"])
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to fetch pr %s (returncode %s)", pr_number, proc.returncode)
                    return False

                proc = Popen([config['paths']['git'], "checkout", "-qf", "FETCH_HEAD"],
                             cwd=self._context["build_path"],
                             env=config["__environment"])
                proc.communicate()
                if proc.returncode != 0:
                    logging.error("failed to checkout pr branch (returncode %s)", proc.returncode)
                    return False

        return True
