#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from fabric.api import local


def docs():
    local("./bin/docs")
    local("./bin/python setup.py upload_sphinx --upload-dir=docs/html")


def release():
    "Update version id in setup.py, changelog and docs/source/conf.py."

    local(
        "python setup.py bdist_egg bdist_wheel sdist "
        "--formats=bztar,gztar,zip upload"
    )

    # TODO: consider https://pypi.python.org/pypi/twine/ for secure uploads.

# TODO: consider https://pypi.python.org/pypi/bumpversion/
