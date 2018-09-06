#!/usr/bin/env python

from setuptools import setup

setup(
    name='Parhelion',
    description='Framework for modeling and generating test datasets',
    author='Tor Solli-Nowlan',
    version='0.1.dev0',
    install_requires=[
        "python-dateutil>=2.7.2",
        "datetime"
    ],
    packages=['parhelion',],
    license='AGPLv3',
)
