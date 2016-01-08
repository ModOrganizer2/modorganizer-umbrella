from unibuild import Project
from unibuild.modules import b2, sourceforge, patch
from unibuild.projects import python
from config import config
import os


boost_version = "1.60.0"
boost_components = [
    "date_time",
    "coroutine",
    "filesystem",
    "python",
    "thread",
    "log",
    "locale"
]


config_template = ("using python : 2.7 : {0}\\PCbuild\\python.exe\n"
                   "  : {0}\\include\n"
                   "  : {0}\\lib\n"
                   "  : <address-model>{1} ;")


Project("boost") \
    .depend(b2.B2().arguments(["address-model={}".format("64" if config['architecture'] == 'x86_64' else "32"),
                               "toolset=msvc-12.0",
                               "link=shared"
                               ] + ["--with-{0}".format(component) for component in boost_components])
            .depend(patch.CreateFile("user-config.jam",
                                     lambda: config_template.format(
                                             os.path.dirname(python.python['build_path']),
                                             "64" if config['architecture'] == "x86_64" else "32")
                                     )
                    .depend(sourceforge.Release("boost",
                                                "boost/{0}/boost_{1}.tar.bz2".format(boost_version,
                                                                                     boost_version.replace(".", "_")),
                                                tree_depth=1))
                    )
            ) \
    .depend("Python")
