__author__ = 'Tannin'


from urldownload import URLDownload


class Release(URLDownload):
    def __init__(self, project, path):
        super(Release, self)\
            .__init__("http://downloads.sourceforge.net/project/{project}/{path}".format(project=project,
                                                                                         path=path))
