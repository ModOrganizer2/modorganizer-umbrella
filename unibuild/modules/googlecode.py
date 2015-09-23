__author__ = 'Tannin'


from urldownload import URLDownload


class Release(URLDownload):
    def __init__(self, project, filename):
        super(Release, self)\
            .__init__("http://{project}.googlecode.com/files/{filename}".format(project=project,
                                                                                filename=filename))
