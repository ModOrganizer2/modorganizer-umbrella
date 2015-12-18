from unibuild.task import Task
import os.path
import shutil


class Replace(Task):

    def __init__(self, filename, search, substitute):
        super(Replace, self).__init__()
        self.__file = filename
        self.__search = search
        self.__substitute = substitute

    @property
    def name(self):
        return "Replace in {}".format(self.__file)

    def process(self, progress):
        full_path = os.path.join(self._context["build_path"], self.__file)
        with open(full_path, "r") as f:
            data = f.read()

        data = data.replace(self.__search, self.__substitute)

        with open(full_path, "w") as f:
            f.write(data)
        return True


class Copy(Task):

    def __init__(self, source, destination):
        super(Copy, self).__init__()
        self.__source = source
        self.__destination = destination

    @property
    def name(self):
        return "Copy {}".format(self.__source)

    def process(self, progress):
        full_source = os.path.join(self._context["build_path"], self.__source)
        full_destination = os.path.join(self._context["build_path"], self.__destination)
        dest_dir = os.path.dirname(full_destination)
        if not os.path.exists(full_destination):
            os.makedirs(full_destination)
        shutil.copy(full_source, full_destination)
        return True


class CreateFile(Task):

    def __init__(self, filename, content):
        super(CreateFile, self).__init__()
        self.__filename = filename
        self.__content = content

    @property
    def name(self):
        return "Create File {}-{}".format(self._context.name, self.__filename)

    def process(self, progress):
        full_path = os.path.join(self._context["build_path"], self.__filename)
        with open(full_path, 'w') as f:
            # the call to str is necessary to ensure a lazy initialised content is evaluated now
            f.write(str(self.__content))

        return True
