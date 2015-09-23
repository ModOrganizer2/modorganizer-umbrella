from unibuild import Project
from unibuild.modules import b2, sourceforge
from config import config


boost_version = "1.58.0"
boost_components = [
    "date_time",
    "coroutine",
    "filesystem",
    "python",
    "thread",
    "log",
    "locale"
]


Project("boost") \
    .depend(b2.B2().arguments(["address-model={}".format("64" if config['architecture'] == 'x86_64' else "32"),
                               "toolset=msvc-12.0"
                               ] + ["--with-{0}".format(component) for component in boost_components])
            .depend(sourceforge.Release("boost",
                                        "boost/{0}/boost_{1}.tar.bz2".format(boost_version,
                                                                             boost_version.replace(".", "_"))))
            )