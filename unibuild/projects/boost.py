from unibuild import Project
from unibuild.modules import b2, sourceforge, build, patch
from unibuild.projects import python
from config import config
import os
from glob import glob
import shutil


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


config_template = ("using python : 2.7 : {0}\\PCbuild\\amd64\\python.exe\n"
                   "  : {0}\\Include\n"
                   "  : {0}\\Lib\n"
                   "  : <address-model>{1} ;")


def install(context):
    for f in glob(os.path.join(context['build_path'], "stage", "lib", "boost_python-*-mt-*.dll")):
        shutil.copy(f, os.path.join(config["__build_base_path"], "install", "bin", "dlls"))
    return True


Project("boost") \
    .depend(build.Execute(install)
            .depend(b2.B2(name="Shared")
                    .arguments(["address-model={}"
                                .format("64" if config['architecture'] == 'x86_64' else "32"),
                                "-a",
                                "-j {}".format(config['num_jobs']),
                                "toolset=msvc-14.0",
                                "link=shared",
                                ] + ["--with-{0}".format(component) for component in boost_components])
                    .depend(b2.B2(name="Static")
                            .arguments(["address-model={}"
                                        .format("64" if config['architecture'] == 'x86_64' else "32"),
                                        "-a",
                                        "-j {}".format(config['num_jobs']),
                                        "toolset=msvc-14.0",
                                        "link=static",
                                        "runtime-link=shared",
                                        ] + ["--with-{0}".format(component) for component in boost_components])
                            .depend(patch.CreateFile("user-config.jam",
                                                     lambda: config_template.format(
                                                     os.path.join(os.path.dirname(python.python['build_path'])),
                                                     "64" if config['architecture'] == "x86_64" else "32")
                                                    )
                                    .depend(sourceforge.Release("boost",
                                                                "boost/{0}/boost_{1}.tar.bz2".format
                                                                (boost_version,boost_version.replace(".", "_")),
                                                                tree_depth=1))
                                    )
                            )
                    )
            .depend("Python")
            )
