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
import os

from config import config
from unibuild import Project
from unibuild.modules import urldownload, build, Patch

# newer versions are beta as of now.  They have slightly (?) different api as well
sevenzip_version = config['7zip_version']
build_path = os.path.join(config['paths']['build'], "7zip-{}".format(sevenzip_version))

# Project("7zip") \
# .depend(Patch.Copy(os.path.join(build_path, "CPP", "7zip", "Bundles", "Format7zF", "{}"
#                                 .format("x86" if config['architecture'] == 'x86' else "AMD64"), "7z.dll"),
#                    os.path.join(config["paths"]["install"], "bin", "dlls"))
#         .depend(build.Run(r"nmake CPU={} NEW_COMPILER=1 MY_STATIC_LINK=1 NO_BUFFEROVERFLOWU=1".format("x86" if config['architecture'] == 'x86' else "AMD64"),
#                           working_directory=os.path.join(build_path, "CPP", "7zip","Bundles", "Format7zF"))
#                 .depend(Patch.Replace("CPP/Build.mak", "-WX", "")
#                         .depend(Patch.Replace("CPP/7zip/Bundles/Format7zF/Format7z.dsp", "-WX", "")
#                                 .depend(urldownload.URLDownload("http://www.7-zip.org/a/7z{}.tar.bz2".format(sevenzip_version.replace(".", "")))
#                                         .set_destination("7zip-{}".format(sevenzip_version)))))))

# 7zip Code for 16.04
# sevenzip is not built here as we only use its source
Project("7zip") \
   .depend(Patch.Copy(os.path.join(build_path, "CPP", "7zip", "Bundles", "Format7zF", "{}"
                                   .format("x86" if config['architecture'] == 'x86' else "AMD64"), "7z.dll"),
                      os.path.join(config["paths"]["install"], "bin", "dlls"))
           .depend(build.Run(r"nmake CPU={} NEW_COMPILER=1 MY_STATIC_LINK=1 NO_BUFFEROVERFLOWU=1".format("x86" if config['architecture'] == 'x86' else "AMD64"),
                             working_directory=os.path.join(build_path, "CPP", "7zip","Bundles", "Format7zF"))
                .depend(Patch.Replace("CPP/Build.mak", "-WX", "")
                    .depend(Patch.Replace("CPP/7zip/Bundles/Format7zF/Format7z.dsp", "-WX", "")
                        .depend(urldownload.URLDownload("http://www.7-zip.org/a/7z{}-src.7z".format(sevenzip_version.replace(".", "")))
                                            .set_destination("7zip-{}".format(sevenzip_version)))))))

