from unibuild.task import Task
import os.path


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


class CreateFile(Task):

    def __init__(self, filename, content):
        super(CreateFile, self).__init__()
        self.__filename = filename
        self.__content = content

    @property
    def name(self):
        return "Create File {}".format(self.__filename)

    def process(self, progress):
        full_path = os.path.join(self._context["build_path"], self.__filename)
        with open(full_path, 'w') as f:
            print(str(self.__content))
            # the call to str is necessary to ensure a lazy initialised content is evaluated now
            f.write(str(self.__content))

        return True
