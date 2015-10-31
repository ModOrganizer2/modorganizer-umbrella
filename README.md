# modorganizer-umbrella
An umbrella- (super-) project for modorganizer.

## Purpose
This repository contains a meta build-system that is able to download and build MO subprojects and dependencies as necessary.
It can be used to build the whole project to produce a build that should be equivalent to the release or to build subprojects (i.e. plugins) with the minimum of dependencies.

This umbrella project can optionally produce ide projects for developers.

## Notes
* While mostly functional this project is work in progress and should only be used by those with the will to spend some time.
* Currently all dependencies are built from source, including monsters like Qt and python. This is necessary to produce releasable bundles (pre-built python would introduce additional run-time dependencies, pre-built Qt doesn't provide debug symbols (pdbs)) but it is overkill if all you want to do is contribute to a plugin.

## Dependencies
* python 2.7
  * decorator
* cmake
* visual C++ 2013 or newer
* 7zip - specifically, the command line version (7za)

## Usage
First, check config and see if all paths are set correctly.

```
usage: unimake.py [-h] [-f FILE] [-d DESTINATION] [target [target ...]]

positional arguments:
  target                make target

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  sets the build script
  -d DESTINATION, --destination DESTINATION
                        output directory (base for download and build)
```

I'd suggest to use a destination folder that isn't too deep, some dependencies don't handle long paths well.
If the make target is left empty, everything is built.
