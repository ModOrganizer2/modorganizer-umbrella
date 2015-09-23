import os.path
import sys
import urllib2


def download(url, filename):
    if os.path.exists(filename):
        return

    data = urllib2.urlopen(url)
    with open(filename, 'wb') as outfile:
        while True:
            block = data.read(4096)
            if not block:
                break
            outfile.write(block)

path = os.path.abspath(os.path.join(os.path.realpath(__file__), os.pardir))

for dep in ["https://pypi.python.org/packages/2.7/n/networkx/networkx-1.10-py2.7.egg",
            "https://pypi.python.org/packages/2.5/p/pydot/pydot-1.0.2-py2.5.egg"]:
    eggpath = os.path.join(path, os.path.basename(dep))
    download(dep, eggpath)
    sys.path.append(eggpath)
