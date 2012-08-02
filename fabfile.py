from fabric.api import local, cd

def docs():
    local("./bin/docs")
    local("./bin/python setup.py upload_sphinx --upload-dir=docs/html")

def release():
    # update version id in setup.py, changelog and docs/source/conf.py
    local("python setup.py sdist --formats=gztar,zip upload")
