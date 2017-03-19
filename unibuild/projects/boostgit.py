from unibuild import Project, Task
from unibuild.modules import b2, git, patch, build
from unibuild.projects import python
from config import config
import os


boost_version = config["boost_version"]
python_version = config["python_version"]
vc_version = config['vc_version']

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

init_repo = build.Run("git submodule init && git submodule update", name="init boost repository" ,working_directory=lambda: os.path.join(config["paths"]["build"], "boost_git")) \
    .set_fail_behaviour(Task.FailBehaviour.CONTINUE) \
    .depend(git.Clone("https://github.com/boostorg/boost.git", "master").set_destination("boost_git"))

Project("boostgit") \
    .depend(b2.B2(name="Shared").arguments(["address-model={}".format("64" if config['architecture'] == 'x86_64' else "32"),
                                            "-a",
                                            "--user-config={}".format(os.path.join(config['paths']['build'],
                                                                                   "boost_git",
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
                                                                                       "boost_git", "user-config.jam")),
                                                "-j {}".format(config['num_jobs']),
                                                "toolset=msvc-" + vc_version,
                                                "link=static",
                                                "runtime-link=shared",
                                                "include={}".format(os.path.join(config['paths']['build'], "icu", "dist", "include", "unicode")),
                                                "-sICU_PATH={}".format(os.path.join(config['paths']['build'], "icu", "dist")),
                                                "-sHAVE_ICU=1",
                                                ] + ["--with-{0}".format(component) for component in boost_components])
                .depend(build.Run(r"b2.exe headers", working_directory=lambda: os.path.join(config["paths"]["build"], "boost_git"))
                    .depend(build.Run(r"bootstrap.bat",working_directory=lambda: os.path.join(config["paths"]["build"], "boost_git")))
                        .depend(patch.CreateFile("user-config.jam",
                                     lambda: config_template.format(
                                         python_version,
                                         os.path.join(python.python['build_path'], "PCBuild",
                                                      "{}".format("" if config['architecture'] == 'x86' else "amd64")).replace("\\",'/'),
                                        os.path.join(python.python['build_path']).replace("\\",'/'),
                                         "64" if config['architecture'] == "x86_64" else "32")
                                     ))

                    .depend(init_repo)

        #            .depend(sourceforge.Release("boost",
        #                                        "boost/{0}/boost_{1}.tar.bz2".format(boost_version,
        #                                                                             boost_version.replace(".", "_")),
        #                                        tree_depth=1))
                    ).depend("icu").depend("Python")
                )
            )
