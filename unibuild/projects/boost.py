from unibuild import Project
from unibuild.modules import b2, sourceforge, Patch, build
from unibuild.projects import python
from config import config
import os
import patch


boost_version = config["boost_version"]
python_version = config["python_version"]
vc_version = config['vc_version_for_boost']

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
                   "  : {0}\n"
                   "  : {1}/python.exe\n"
                   "  : {2}/Include\n"
                   "  : {1}\n"
                   "  : <address-model>{3}\n"
                   "  : <define>BOOST_ALL_NO_LIB=1\n"
                   "  ;")


def patchboost(context):
    try:
        savedpath = os.getcwd()
        os.chdir(os.path.join("{}/boost_{}".format(config["paths"]["build"], config["boost_version"].replace(".", "_"))))
        pset = patch.fromfile(os.path.join(config["paths"]["build"], "usvfs", "patches", "type_traits_vs15_fix.patch"))
        pset.apply()
        os.chdir(savedpath)
        return True
    except OSError:
        return False

Project("boost") \
    .depend(Patch.Copy(os.path.join("{}/boost_{}/stage/lib/boost_python-vc{}-mt-{}.dll"
                                    .format(config["paths"]["build"],
                                            config["boost_version"].replace(".", "_"),
                                            vc_version.replace(".",""),
                                            "_".join(boost_version.split(".")[:-1])
                                            )),
                       os.path.join(config["paths"]["install"], "bin"))
    .depend(b2.B2(name="Shared").arguments(["address-model={}".format("64" if config['architecture'] == 'x86_64' else "32"),
                                            "-a",
                                            "--user-config={}".format(os.path.join(config['paths']['build'],
                                                                                   "boost_{}".format(boost_version.
                                                                                                   replace(".", "_")),
                                                                                   "user-config.jam")),
                                            "-j {}".format(config['num_jobs']),
                                            "toolset=msvc-" + vc_version,
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
                                                "toolset=msvc-" + vc_version,
                                                "link=static",
                                                "runtime-link=shared",
                                                "include={}".format(os.path.join(config['paths']['build'], "icu", "dist", "include", "unicode")),
                                                "-sICU_PATH={}".format(os.path.join(config['paths']['build'], "icu", "dist")),
                                                "-sHAVE_ICU=1",
                                                ] + ["--with-{0}".format(component) for component in boost_components])
            .depend(Patch.CreateFile("user-config.jam",
                                     lambda: config_template.format(
                                         python_version,
                                         os.path.join(python.python['build_path'], "PCBuild",
                                                      "{}".format("" if config['architecture'] == 'x86' else "amd64")).replace("\\",'/'),
                                        os.path.join(python.python['build_path']).replace("\\",'/'),
                                         "64" if config['architecture'] == "x86_64" else "32")
                                     ).depend(build.Execute(patchboost)
                    .depend(sourceforge.Release("boost",
                                                "boost/{0}/boost_{1}.tar.bz2".format(boost_version,
                                                                                     boost_version.replace(".", "_")),
                                                tree_depth=1))
                    ).depend("icu").depend("Python")
                )
            )
            )
            )