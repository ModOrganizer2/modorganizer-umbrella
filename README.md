# modorganizer-umbrella
An umbrella- (super-) project for modorganizer.

## Purpose
This repository contains a meta build-system that is able to downloads MO subprojects and dependencies as necessary.

## Dependencies
* python
* * decorator
* cmake
* visual C++ 2013 or newer
* graphviz

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

I'd suggest to use a destination folder that isn't too deep, some dependencies well with long paths.
If the make target is left empty, everything is built.
