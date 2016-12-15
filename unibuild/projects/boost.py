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


config_template = ("using python\n"
                   "  : 2.7\n"
                   "  : {0}/python.exe\n"
                   "  : {1}/Include\n"
                   "  : {0}\n"
                   "  : <address-model>{2}\n"
                   "  : <define>BOOST_ALL_NO_LIB=1\n"
                   "  ;")

Project("boost") \
    .depend(b2.B2(name="Shared").arguments(["address-model={}".format("64" if config['architecture'] == 'x86_64' else "32"),
                                            "-a",
                                            "--user-config={}".format(os.path.join(config['paths']['build'],
                                                                                   "boost_{}".format(boost_version.
                                                                                                   replace(".", "_")),
                                                                                   "user-config.jam")),
                                            "-j {}".format(config['num_jobs']),
                                            "toolset=msvc-14.0",
                                            "link=shared",
                                            "include={}".format(os.path.join(config['paths']['build'], "icu", "dist", "include", "unicode")),
                                            "-sICU_PATH={}".format(
                                                os.path.join(config['paths']['build'], "icu", "dist")),
                                            "-sHAVE_ICU=1",
                                            ] + ["--with-{0}".format(component) for component in boost_components])
        .depend(b2.B2(name="Static").arguments(["address-model={}".format("64" if config['architecture'] == 'x86_64' else "32"),
                                                "-a",
                                                "--user-config={}".format(os.path.join(config['paths']['build'],
                                                                                       "boost_{}".format(boost_version.
                                                                                                       replace(".", "_")), "user-config.jam")),
                                                "-j {}".format(config['num_jobs']),
                                                "toolset=msvc-14.0",
                                                "link=static",
                                                "runtime-link=shared",
                                                "include={}".format(os.path.join(config['paths']['build'], "icu", "dist", "include", "unicode")),
                                                "-sICU_PATH={}".format(os.path.join(config['paths']['build'], "icu", "dist")),
                                                "-sHAVE_ICU=1",
                                                ] + ["--with-{0}".format(component) for component in boost_components])
            .depend(patch.CreateFile("user-config.jam",
                                     lambda: config_template.format(
                                         os.path.join(python.python['build_path'], "PCBuild",
                                                      "{}".format("" if config['architecture'] == 'x86' else "amd64")).replace("\\",'/'),
                                        os.path.join(python.python['build_path']).replace("\\",'/'),
                                         "64" if config['architecture'] == "x86_64" else "32")
                                     )
                    .depend(sourceforge.Release("boost",
                                                "boost/{0}/boost_{1}.tar.bz2".format(boost_version,
                                                                                     boost_version.replace(".", "_")),
                                                tree_depth=1))
                    ).depend("icu").depend("Python")
                )
            )