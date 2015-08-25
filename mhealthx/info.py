#!/usr/bin/env python
"""
This file contains parameters for mHealthX to fill settings in setup.py,
the mHealthX top-level docstring, and for building any docs.
In setup.py we execute this file, so it cannot import mHealthX.
"""

# Mindboggle version information.  An empty version_extra corresponds to a
# full release.  '.dev' as a version_extra string means a development version
version_major = 1
version_minor = 0
version_micro = 0
version_extra = '.dev'

# Format expected by setup.py and doc/source/conf.py: string of form "X.Y.Z"
__version__ = "%s.%s.%s%s".format(version_major,
                                  version_minor,
                                  version_micro,
                                  version_extra)

CLASSIFIERS = ["Development Status :: 3 - Alpha",
               "Environment :: Console",
               "Intended Audience :: Science/Research",
               "License :: OSI Approved :: Apache v2.0",
               "Operating System :: OS Independent",
               "Programming Language :: Python",
               "Topic :: Scientific/Engineering"]

description  = "feature extraction of mHealth data"

# Note: this long_description is actually a copy/paste from the top-level
# README.rst, so that it shows up nicely on PyPI.  So please remember to edit
# it only in one place and sync it correctly.
long_description = """
========
mHealthX
========

mHealthX is a package for automated feature extraction of mobile health app data.

Code
====

You can find our sources and single-click downloads:

* `Main repository`_ on Github.
* Downloads of all `available releases`_.

.. _main repository: http://github.com/binarybottle/mhealthx
.. _available releases: http://github.com/binarybottle/mhealthx/downloads

License
=======

mHealthX is licensed under the terms of the Apache v2.0 license.

"""

# versions for dependencies
#NUMPY_MIN_VERSION='1.2'

# Main setup parameters
NAME                = 'mHealthX'
MAINTAINER          = "Arno Klein"
MAINTAINER_EMAIL    = "arno@sagebase.org"
DESCRIPTION         = description
LONG_DESCRIPTION    = long_description
URL                 = "http://github.com/binarybottle/mhealthx"
DOWNLOAD_URL        = "http://github.com/binarybottle/mhealthx"
LICENSE             = "Apache v2.0"
CLASSIFIERS         = CLASSIFIERS
AUTHOR              = "Arno Klein"
AUTHOR_EMAIL        = "arno@sagebase.org"
PLATFORMS           = "OS Independent"
MAJOR               = version_major
MINOR               = version_minor
MICRO               = version_micro
ISRELEASE           = version_extra
VERSION             = __version__
PROVIDES            = ["mhealthx"]
REQUIRES            = [] #["numpy (>={0})".format(NUMPY_MIN_VERSION)]

