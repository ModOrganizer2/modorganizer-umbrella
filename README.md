# modorganizer-umbrella
An umbrella- (super-) project for [modorganizer](https://github.com/LePresidente/modorganizer).

## How to build ModOrganizer 2

If you have questions or you need help visit us in our [Discord](https://discord.gg/cYwdcxj) or write in the [STEP forum thread](http://forum.step-project.com/topic/12538-wip-how-to-build-modorganizer-using-modorganizer-umbrella/).:

## Purpose
This repository contains a meta build-system that is able to download and build MO subprojects and dependencies as necessary.
It can be used to build the whole project to produce a build that should be equivalent to the release or to build subprojects (i.e. plugins) with the minimum of dependencies.

This umbrella project can optionally produce ide projects for developers.

## Notes
* While mostly functional this project is work in progress and should only be used by those with the will to spend some time.
* Currently all dependencies are built from source, including monsters like Qt and python. This is necessary to produce releasable bundles (pre-built python would introduce additional run-time dependencies, pre-built Qt doesn't provide debug symbols (pdbs)) but it is overkill if all you want to do is contribute to a plugin.

## Concept
At its base this is actually a fairly simple program. Arbitrary command calls are wrapped inside Task objects (grouped as projects) and put into a dependency graph.
The tasks are then executed in proper order, with the umbrella providing the environment so you don't need to have all required tool in your global PATH variable.

There are specialised task implementations to conveniently specify sources to be retrieved from a repository or to get the correct make tool invoked.

Now one thing that may be a bit confusing is that all tasks have to be fully initialized before processing starts but since tasks will usually build upon each other, not all information may be available at that time.
In these cases functions/lambdas can be passed as parameters in task initialization which will then be invoked when that task is processed which will be after all dependencies are complete.

Some more details:
- Successfully completed tasks are memorized (in the "progress" directory) and will not be run again
- Names for tasks are generated so they may not be very user-friendly
- Technically, independent tasks could be executed in parallel but that is not (yet) implemented

## Usage
```
usage: unimake.py [-h] [-f file] [-d path] [-s option=value] [-g]
                  [-b directory] [-p directory] [-i directory]
                  [target [target ...]]

positional arguments:
  target                make this target. eg: modorganizer-archive
                        modorganizer-uibase (you need to delete the progress
                        file. will be fixed eventually)

optional arguments:
  -h, --help            show this help message and exit
  -f file, --file file  sets the build script file. eg: -f makefile.uni.py
  -d path, --destination path
                        output directory for all generated folder and files
                        .eg: -d E:/MO2
  -s option=value, --set option=value
                        set configuration parameters. most of them are in
                        config.py. eg: -s paths.build=build
  -g, --graph           update dependency graph
  -b directory, --builddir directory
                        sets build directory. eg: -b build
  -p directory, --progressdir directory
                        sets progress directory. eg: -p progress
  -i directory, --installdir directory
                        set install directory. eg: .i directory
```
I'd suggest to use a destination folder that isn't too deep, some dependencies don't handle long paths well.
If the make target is left empty, everything is built.
