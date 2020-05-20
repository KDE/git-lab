#!/usr/bin/env python3

import subprocess

from setuptools import setup, find_packages
from setuptools.command.install import install

VERSION: str = "0.1"


class GitLabInstallCommand(install):
    """
    Customized install command, which allows us to generate a man page
    """

    def run(self):
        install.run(self)

        help2man_found = False
        try:
            subprocess.check_call(["which", "help2man"])
            help2man_found = True
        except subprocess.CalledProcessError:
            help2man_found = False

        if help2man_found:
            print("Found optional dependency help2man - generating man page")
            subprocess.call(
                [
                    "help2man",
                    "--no-info",
                    "--version-string={}".format(VERSION),
                    "git-lab",
                    "--output",
                    "/usr/local/share/man/man1/git-lab.1",
                ]
            )
        else:
            print("Could not find optional dependency help2man - not generating a man page")


setup(
    name="lab",
    version=VERSION,
    packages=find_packages(),
    cmdclass={"install": GitLabInstallCommand,},
    entry_points={"console_scripts": ["git-lab = lab:main",]},
    install_requires=open("requirements.txt").readlines(),
)
