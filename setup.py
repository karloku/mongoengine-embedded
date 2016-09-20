# -*- coding: utf-8 -*-
import re
import ast
from pkg_resources import Requirement, RequirementParseError
from setuptools import setup, find_packages


def load_requirements():
    from os import path
    from itertools import imap

    def is_requirement(line):
        try:
            Requirement.parse(line)
            return True
        except (RequirementParseError, ValueError) as e:
            return False

    fname = path.join(path.dirname(__file__), 'requirements.txt')
    with open(fname, 'r') as requirements:
        return filter(is_requirement, imap(str.strip, requirements))


def find_version():
    _version_re = re.compile(r'__version__\s+=\s+(.*)')

    with open('mongoengine_embedded/__version__.py', 'rb') as f:
        return str(ast.literal_eval(_version_re.search(
            f.read().decode('utf-8')).group(1)))


def read(fname):
    with open(fname, 'rb') as f:
        return f.read()

setup(
    name='mongoengine-embedded',
    version=find_version(),
        description=('Access embedded documents with CRUD by id.'),
    long_description=read("README.md"),
    author='Karloku Sang',
    author_email='karloku@loku.it',
    url='https://github.com/karloku/mongoengine-embedded',
    packages=find_packages(exclude=("test*", 'examples')),
    package_dir={'mongoengine-embedded': 'mongoengine_embedded'},
    install_requires=load_requirements(),
    license="MIT",
    zip_safe=False)
