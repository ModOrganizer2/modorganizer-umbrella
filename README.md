<!-- [![Python Check status](https://ci.appveyor.com/api/projects/status/ev4wj7qmscr5b09d?svg=true)](https://ci.appveyor.com/project/Modorganizer2/modorganizer-umbrella) -->
[![No Maintenance Intended](https://unmaintained.tech/badge.svg)](https://unmaintained.tech/)

> Tthis repository is archived and obsolete, see
> https://github.com/ModOrganizer2/mob if you want to build ModOrganizer2.


# modorganizer-umbrella
An umbrella- (super-) project for [modorganizer](https://github.com/Modorganizer2/modorganizer).

## How to build ModOrganizer 2

Mod Organizer requires a Windows 64 bit Machine because it is a 64bit binary.

If you have questions or you need help visit us in our [Discord](https://discord.gg/cYwdcxj) or write in the [STEP forum thread](http://forum.step-project.com/topic/12538-wip-how-to-build-modorganizer-using-modorganizer-umbrella/).:

### Clone Repository

First you need to clone the umbrella repository. We recommend that you clone it into the root of your C:\ drive.
Open there a console and copy in: ``git clone https://github.com/Modorganizer2/modorganizer-umbrella``

### Software Requirements
Now you need to install all required software to build Mod Organizer.

#### Manual Requirements
* Qt 5.15.2: [Download Manager](http://download.qt.io/official_releases/online_installers/qt-unified-windows-x86-online.exe)
  #### Qt Packages required:
  * msvc2019-64
  * qtwebengine
  * Optional: Sources and Windows debug files
  
  Be sure to expand the options to show ALL the available choices and then select those packages. Failure to do so will result in a missing qmake.exe error or other build errors.
* Visual Studio Community 2019: [Download Link](https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&rel=16)
  #### Visual Studio Packages required:
  * .NET desktop development
  * Desktop development for C++
  
  Additionally you need to activate under Individual components:
  * "Windows Universal C Runtime" (Under SDKs, libraries, and frameworks)
  * "Windows 10 SDK (10.0.19041.0) for Desktop C++ \[x86 and x64\]" (Under SDKs, libraries, and frameworks)
  * C++ ATL for v141/v142 build tools (x86 & x64) (Under SDKs, libraries, and frameworks)
  * Ensure v141 build tools are selected for some dependencies that may not support v142 yet
    * *v141 build tools may no longer be needed*
    * Note: If you have problems building Python due to a "missing SDK version", edit the registry key \[HKEY_LOCAL_MACHINE\\SOFTWARE\\WOW6432Node\\Microsoft\\Microsoft SDKs\\Windows\\v10.0\] to point to the the 10.0.19041.0 SDK.
* .NET Framework 3.5: [Download Link](https://www.microsoft.com/en-us/download/details.aspx?id=21)
  * *This is a dependency of the NCC install tool, which may be deprecated soon*

#### Additional Requirements
##### Manual Install
* 7zip (Latest 64Bit): [Download Link](https://www.7-zip.org/a/7z1900-x64.exe)
* Inno 5 or 6 (Only required to build Installer): [Download Link](https://www.jrsoftware.org/download.php/is.exe)
* CMake (latest 64bit):  [Download Link](https://github.com/Kitware/CMake/releases/download/v3.18.3/cmake-3.18.3-win64-x64.msi)
* Git: [Download Link](https://github.com/git-for-windows/git/releases/download/v2.28.0.windows.1/Git-2.28.0-64-bit.exe)
* Python 3 (64Bit): [Download Link](https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe)
  * *If you've previously used a Python 2 version of Umbrella, you may need to run `git clean -xdf` to remove cached data which interferes with Python 3.*
* Strawberry Perl: [Download Link](http://strawberryperl.com/download/5.32.0.1/strawberry-perl-5.32.0.1-64bit.msi)
##### Chocolatey
Optionally, you can use [Chocolatey](https://chocolatey.org/install) to install these dependencies. The packages are:
* 7zip
* cmake
* git
* InnoSetup
* python
* strawberyperl

#### Build
Now we  can finally start the build process. Just run the following command in the modorganizer-umbrella folder: ``python.exe unimake.py``

You can specify a build location using ``-d <directory path>``

If you wish to rebuild only one target once everything is complete, you simply delete the relevant txt file or directory in the progress folder, e.g C:\modorganizer-umbrella\progress\modorganizer
Then rerun the build script and it will rebuild the relevant project.

To build an individual project once the umbrella script has completed successfully, you can also use the relative VS solution, making sure to set the configuration to RelWithDebugInfo.

## Purpose
This repository contains a meta build-system that is able to download and build MO subprojects and dependencies as necessary.
It can be used to build the whole project to produce a build that should be equivalent to the release or to build subprojects (i.e. plugins) with the minimum of dependencies.

This umbrella project can optionally produce IDE projects for developers.

## Notes
* While mostly functional this project is work in progress and should only be used by those with the will to spend some time.
* Currently all dependencies (except, optionally, Qt) are built from source, including monsters like Boost and Python. This is necessary to produce releasable bundles (pre-built python would introduce additional run-time dependencies, pre-built Qt doesn't provide debug symbols (pdbs)) but it is overkill if all you want to do is contribute to a plugin.

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
                        set install directory. eg: -i directory
```
I'd suggest to use a destination folder that isn't too deep, some dependencies don't handle long paths well.
If the make target is left empty, everything is built. A incomplete lists of targets can be found [here](targets.md).

Here are the dependency graphs that currently unimake takes care of: https://www.dropbox.com/s/rqi1wrboevrxelu/graph.pdf?dl=1
