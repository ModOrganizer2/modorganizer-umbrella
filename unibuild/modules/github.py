__author__ = 'Tannin'


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
    def __init__(self, author, project, tag):
        super(Source, self).__init__("https://github.com/{author}/{project}.git".format(author=author,
                                                                                        project=project,
                                                                                        tag=tag), "master")
        #super(Source, self).__init__("https://github.com/{author}/{project}/archive/{tag}.zip".format(), 1)
        # don't use the tag as the file name, otherwise we get name collisions on "master" or other generic names
        #self.set_destination(project)
