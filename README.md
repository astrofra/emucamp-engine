emucamp-engine
==============

A scripted toolchain to automatically update a database of listed emulators, including each binary of each version.

The project is divided in two parts :

1. The Engine
2. The website

The whole engine is open-sourced in order to avoid the complete oblivion in case the maintainer is not able to work anymore on the project.

1. The Engine
=============

The Engine is a set of Python scripts able to crawl on a given list of sources, fetch any updated data, and download the data that changed since the last run. The sources are described using simple text files with a very basic syntax.

Once the run is done, the result is a tree of folders, containing each version of each emulator, sorted by original machines (C64, CPC, Amiga, Atari...)

Each machine (or emulator) shows a description in English language, extracted from Wikipedia.
The extract can be automated using the Wikipedia API.
https://www.mediawiki.org/wiki/API:Main_page

Each emulator can be downloaded using one or several urls.
The binaries could be either :
 - directly linked to the original emulator's site
 - downloaded from the site and hosted on emucamp.net
 - found by the visitors by following an external link to the original emulator's website

1.a Setup
---------

You need python and pip.
Get python on http://www.python.org/
Get pip on http://www.pip-installer.org/

Once you have python and pip installed, you can run:
```bash
pip install -r requirements.txt
```
It will install the python modules required by the project.

1.b Run
-------

To update the website, run:
```bash
python python/main.py
```

To update the meta ratings, run:
```bash
python python/meta_ratings.py
```

Under Windows you can run the provided bat scripts:
```bash
start.bat
```
and
```bash
start_meta_ratings.bat
```

 2. The website
===============

 The website is a static site (pure HTML, no PHP, no SQL). Everything is built on the local machine that runs the engine, and then uploaded to a given location.

 The files are a mix or html, css, png and binary files.

 ![](http://www.astrofra.com/posts/misc/2014-07-20_080904.jpg)
