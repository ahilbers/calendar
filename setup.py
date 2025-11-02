#!/usr/bin/env python

import pathlib
from setuptools import setup

setup(
    name="schedules",
    version="0.0",
    author="Adriaan Hilbers",
    author_email="a.hilbers@icloud.com",
    packages=["schedules"],
    install_requires=pathlib.Path("requirements.txt").read_text().strip().split("\n"),
)
