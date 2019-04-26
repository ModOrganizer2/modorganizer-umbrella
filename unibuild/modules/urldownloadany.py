# Copyright (C) 2019 Mod Organizer contributors.
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

from unibuild.retrieval import Retrieval
from unibuild.modules.urldownload import URLDownload
import urllib.error

class URLDownloadAny(Retrieval):
  '''Downloads and uses any of the available downloads from a given tuple of URLDownload objects.'''

  def __init__(self, url_list, tree_depth=0):
    assert isinstance(url_list, tuple), "url_list must be a tuple"
    assert len(url_list) > 0, "url_list can not be empty"
    for url in url_list:
      assert isinstance(url, URLDownload), "url must be a URLDownload"

    super(URLDownloadAny, self).__init__()
    self.__url_list = url_list
    self.__tree_depth = tree_depth

  @property
  def name(self):
    return self.__url_list[0].name

  def set_destination(self, destination_name):
    for url in self.__url_list:
      url.set_destination(destination_name)
    return self

  def prepare(self):
    for url in self.__url_list:
      url.set_context(self._context)
      url.prepare()

  def process(self, progress):
    for url in self.__url_list:
      try:
        if url.process(progress):
          return True
      except (urllib.error.HTTPError, urllib.error.URLError):
          continue
    return False

  def download(self, output_file_path, progress):
    for url in self.__url_list:
      try:
        url.download(output_file_path, progress)
      except (urllib.error.HTTPError, urllib.error.URLError):
        continue
