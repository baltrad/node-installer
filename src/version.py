import os

from gitutil import git_describe


VERSION_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "etc/version"
)

def set_offline_node_version():
    open(VERSION_FILE, "w").write(git_describe())

##
# get node version either from ../etc/version or from git tag
# or as a final resort just name the version "SNAPSHOT".
#
def get_node_version():
    version_file = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "etc/version"
    )
    if os.path.exists(version_file):
        return open(version_file).read().strip(" \r\n")
    else:
        try:
          return git_describe()
        except:
          return("SNAPSHOT")

