# Copyright (C) 2015 Sebastian Herbord. All rights reserved.
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


from git import Clone
from urldownload import URLDownload


class Release(URLDownload):
    def __init__(self, author, project, version, filename, extension="zip", tree_depth=0):
        super(Release, self) \
            .__init__("https://github.com/{author}/{project}/releases/download/{version}/"
                      "{filename}.{extension}".format(author=author,
                                                      project=project,
                                                      version=version,
                                                      filename=filename,
                                                      extension=extension), tree_depth)


class Source(Clone):
    def __init__(self, author, project, branch="master", super_repository=None, update=True, commit=None, shallowclone=False):
        super(Source, self).__init__("https://github.com/{author}/{project}.git".format(author=author,
                                                                                        project=project),
                                     branch, super_repository, update, commit,shallowclone)
        # super(Source, self).__init__("https://github.com/{author}/{project}/archive/{tag}.zip".format(), 1)
        # don't use the tag as the file name, otherwise we get name collisions on "master" or other generic names
        # self.set_destination(project)

# TODO never supported checking out by tag, should create new class here. (required by asmjit)
