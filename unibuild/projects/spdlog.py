from config import config
from unibuild import Project
from unibuild.modules import cmake, github, build

spdlog_version = config['spdlog_version']

Project("spdlog") \
    .depend(github.Tag("gabime", "spdlog", spdlog_version, "", tree_depth=1))
