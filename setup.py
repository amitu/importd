# -*- coding: utf-8 -*-
#
# To Upload to PyPI by executing:  python3 setup.py sdist upload -r pypi


"""Setup.py for Python, as Generic as possible."""


import os
from setuptools import setup


try:
    long_description = open('README.rst', 'rt').read()
    long_description += open('ChangeLog.rst', 'rt').read()
except Exception:
    long_description = ""


MODULE_PATH = os.path.join(os.getcwd(), "importd", "__init__.py")


def find_this(search, filename=MODULE_PATH):
    """Take a string and a filename path string and return the found value."""
    if not search:
        return
    for line in open(str(filename)).readlines():
        if search.lower() in line.lower():
            line = line.split("=")[1].strip()
            if "'" in line or '"' in line or '"""' in line:
                line = line.replace("'", "").replace('"', '').replace('"""', '')
            return line


setup(
    name="importd",
    description="A django based miniframework, inspired by Sinatra",
    long_description=long_description,

    version=find_this("__version__"),

    author=find_this("__author__"),
    author_email=find_this("__email__"),
    maintainer=find_this("__author__"),
    maintainer_email=find_this("__email__"),

    url=find_this("__source__"),
    license=find_this("__license__"),


    install_requires=[
        "fhurl>=0.1.7", "smarturls", "six", "Django>=1.3",
        "dj-database-url", "path.py"
    ],


    packages=["importd"],
    zip_safe=True,


    keywords=['Django', 'Miniframework', 'ImportD', 'Web', 'Minimalism'],


    classifiers=[

        'Development Status :: 5 - Production/Stable',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',

        'Natural Language :: English',

        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',

        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',

        'Programming Language :: Python :: Implementation :: CPython',

        'Topic :: Software Development',

    ],
)
