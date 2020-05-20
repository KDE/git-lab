#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="lab",
    version="0.1",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "git-lab = lab:main",
        ]
    },
    install_requires=open("requirements.txt").readlines()
)
