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


from urldownload import URLDownload
from git import Clone


class Release(URLDownload):
    def __init__(self, author, project, version, filename, extension="zip"):
        super(Release, self) \
            .__init__("https://github.com/{author}/{project}/releases/download/{version}/"
                      "{filename}.{extension}".format(author=author,
                                                      project=project,
                                                      version=version,
                                                      filename=filename,
                                                      extension=extension))


class Source(Clone):
    def __init__(self, author, project, tag, super_repository=None, update=True):
        super(Source, self).__init__("https://github.com/{author}/{project}.git".format(author=author,
                                                                                        project=project,
                                                                                        tag=tag),
                                     "master", super_repository, update)
        #super(Source, self).__init__("https://github.com/{author}/{project}/archive/{tag}.zip".format(), 1)
        # don't use the tag as the file name, otherwise we get name collisions on "master" or other generic names
        #self.set_destination(project)

