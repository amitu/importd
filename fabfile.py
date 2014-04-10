# -*- coding: utf-8 -*-


from fabric.api import local


def docs():
    """Generate the Docs"""
    local("./bin/docs")
    local("./bin/python setup.py upload_sphinx --upload-dir=docs/html")


def release():
    """Make Release"""
    # update version id in setup.py, changelog and docs/source/conf.py
    local("python setup.py sdist --formats=gztar,zip upload")
