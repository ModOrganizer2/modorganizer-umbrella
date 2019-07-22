from config import config
from unibuild import Project
from unibuild.modules import cmake, github, build

fmt_version = config['fmt_version']

Project("fmt") \
  .depend(cmake.CMake().arguments(["-DCMAKE_BUILD_TYPE={0}".format(config["build_type"]), "-DFMT_TEST=OFF", "-DFMT_DOC=OFF"])
    .depend(github.Release("fmtlib", "fmt", fmt_version, "fmt-" + fmt_version, tree_depth=1)))

