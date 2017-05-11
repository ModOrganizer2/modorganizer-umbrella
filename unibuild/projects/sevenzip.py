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


from unibuild import Project
from unibuild.modules import urldownload, build, Patch
from config import config
import os


# newer versions are beta as of now. They have slightly (?) different api as well
sevenzip_version = "16.04"

# TODO build sevenzip, we require the dll in install/bin/dlls.
# sevenzip is not built here as we only use its source
Project("7zip") \
        .depend(Patch.Copy(os.path.join(config['paths']['build'], "7zip", "CPP", "7zip", "Bundles", "Format7zF", "{}"
                                        .format("x86" if config['architecture'] == 'x86' else "AMD64"),"7z.dll"),
                           os.path.join(config["paths"]["install"], "bin","dlls"))
                .depend(build.Run(r"nmake CPU={} NEW_COMPILER=1 MY_STATIC_LINK=1 NO_BUFFEROVERFLOWU=1".format("x86" if config['architecture'] == 'x86' else "AMD64"),
                      working_directory=os.path.join(config['paths']['build'], "7zip", "CPP", "7zip"))
                .depend(urldownload.URLDownload("http://www.7-zip.org/a/7z{}-src.7z".format(sevenzip_version.replace(".", ""))).set_destination("7zip"))))
