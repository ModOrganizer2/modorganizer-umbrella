import os.path
import sys
import urllib2
import pip
import tarfile
from subprocess import call


def download(url, filename):
    if os.path.exists(filename):
        return False

    data = urllib2.urlopen(url)
    with open(filename, 'wb') as outfile:
        while True:
            block = data.read(4096)
            if not block:
                break
            outfile.write(block)
    return True

path = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))


for dep in ["https://pypi.python.org/packages/2.7/n/networkx/networkx-1.10-py2.7.egg",
            "https://pypi.python.org/packages/2.5/p/pydot/pydot-1.0.2-py2.5.egg",
            "https://gitlab.com/LePresidente/python-build-tools/uploads/2f0b7e8340f635002842bb500eb4cb9f/Jinja2-2.9.5-py2.7.egg",
            "https://gitlab.com/LePresidente/python-build-tools/uploads/18a195f7945ca35ad563b428739f254b/buildtools-0.0.2-py2.7.egg",
            "https://gitlab.com/LePresidente/python-build-tools/uploads/e6307543843150e8896194b5cd4e2630/MarkupSafe-1.0-py2.7.egg",
            "https://gitlab.com/LePresidente/python-build-tools/uploads/acf5c7f04e84046f42a812477ed74d76/psutil-5.2.1-py2.7-win-amd64.egg",
            "https://gitlab.com/LePresidente/python-build-tools/uploads/893dfff5db3aa30fe19e262becce5245/six-1.10.0-py2.7.egg",
            "https://gitlab.com/LePresidente/python-build-tools/uploads/ad42c9699d5a9e842eeda8ccc291fdda/PyYAML-3.12-py2.7-win-amd64.egg",
            "https://gitlab.com/LePresidente/python-build-tools/uploads/f280239f8b89713e0b35f038eca151fe/lxml-3.5.0-py2.7-win-amd64.egg"]:
    eggpath = os.path.join(path, os.path.basename(dep))
    download(dep, eggpath)
    sys.path.append(eggpath)

for dep in ["decorator"]:
    destpath = "{0}/{1}".format(path, dep)
    if not os.path.exists(destpath):
        pip.main(["install", "--target={0}".format(destpath), dep])
    sys.path.append(destpath)

""" neither of these work. particularly building pygraphviz requires a specific VC version in a specific location


for dep in ["pygraphviz"]:
    pip.main(["install", "--install-option=\"--prefix={}\"".format(path), dep])


for dep in ["https://pypi.python.org/packages/source/p/pygraphviz/pygraphviz-1.3.1.tar.gz"]:
    basename = os.path.basename(dep)
    libpath = os.path.join(path, basename)
    if download(dep, libpath):
        with tarfile.open(libpath, 'r') as tar:
            tar.extractall(path=path)
        cwd = os.path.join(path, os.path.splitext(os.path.splitext(basename)[0])[0])
        call(["python", "setup.py", "install"], cwd=cwd)
"""
