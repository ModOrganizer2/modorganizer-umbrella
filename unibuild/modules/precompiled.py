# Copyright (C) 2015 Sebastian Herbord.  All rights reserved.
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
from config import config
from unibuild.modules.github import Release
from unibuild.modules.urldownload import URLDownload

class dep(Release):
    def __init__(self, project, version, filename, extension="7z", tree_depth=0):
        if config['use_dependencies_repo']:
            URLDownload.__init__(self, "https://github.com/{author}/modorganizer-deps/blob/master/{project}/{filename}.{extension}/?raw=true" \
                .format(author = config['dependencies_releases_author'],
                        project = project, filename = filename,
                        extension = extension), tree_depth)
        else:
            Release.__init__(config['Main_Author'], project, version, filename, extension, tree_depth)

    def __getitem__(self, config, key):
        return config.config[key]
