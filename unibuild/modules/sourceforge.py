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
from unibuild.modules.urldownload import URLDownload
import requests
import re

class Release(URLDownload):
    def __init__(self, project, path, tree_depth=0):
        r = requests.get("https://sourceforge.net/projects/{project}/files/{path}/download".format(project=project, path=path), headers={'User-Agent': 'curl/7.37.0'}, allow_redirects=True)
        final_path = r.url
        d = r.headers.get('content-disposition', None)
        fname = None
        if d:
            fname = re.findall("filename=(.+)", d)[0]
        super(Release, self) \
            .__init__(final_path, tree_depth, name=fname if fname else None)
