# See https://packaging.python.org/en/latest/distributing.html
# and https://docs.python.org/2/distutils/setupscript.html
# and https://pypi.python.org/pypi?%3Aaction=list_classifiers

import os
from setuptools import setup, find_packages


def read_file(path):
    with open(path, "rb") as f:
        contents = f.read()
        f.close()
    return contents


def get_description():
    files = ("README", "COPYING", "CHANGES", "TODO")
    extensions = ("md", "rst", "txt")

    description = ""
    for file_name in files:
        for ext in extensions:
            path = "%s.%s" % (file_name, ext)
            if os.path.exists(path):
                description += read_file(path)

    return description


def get_requirements():
    content = read_file("requirements.pip")
    dependencies = list()
    for package in content.split("\n"):
        if len(package) == 0:
            continue

        # HACK: setup() does not support package links in the same way as pip.
        # Here, we check for a -e and remove 7 characters for "-e git+". This is
        # of course very brittle. Also, it doesn't work even using
        # ``dependency_links``.
        # See http://stackoverflow.com/a/12151180/241720

        if package[:2] == "-e":
            pass
            # dependencies.append(package[7:])
        else:
            dependencies.append(package)

    return dependencies


def get_version():
    return read_file("VERSION.txt")


setup(
    name='sphinx-helpers',
    version=get_version(),
    description='Common helpers for creating documentation with Sphinx.',
    long_description=get_description(),
    author='Shawn Davis',
    author_email='shawn@ptltd.co',
    url='https://bitbucket.org/develmaycare/sphinx-helpers',
    packages=find_packages(),
    install_requires=get_requirements(),
    classifiers=[
        'Development Status :: 2 - Pre Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
    ],
    zip_safe=False,
    tests_require=get_requirements(),
    test_suite='runtests.runtests'
)