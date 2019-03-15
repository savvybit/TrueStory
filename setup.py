#! /usr/bin/env python3


import os
from pathlib import Path

from setuptools import find_packages, setup


def read(fpath):
    check = os.path.isfile
    path = Path(__file__).parent / fpath
    if not check(path):
        path = fpath
        if not check(path):
            return None
    with open(path) as stream:
        return stream.read().strip()


def get_requirements(path="requirements.txt"):
    data = read(path)
    lines = []
    if not data:
        return lines
    for line in data.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-r"):
            new_path = line[2:].strip()
            lines.extend(get_requirements(path=new_path))
            continue
        lines.append(line)
    return lines


setup(
    name="truestory",
    version="0.1.0",
    description="Get the both sides of news.",
    long_description=read("README.md") or "",
    url="https://github.com/SavvyBit/TrueStory",
    license="MIT",
    author="SavvyBit",
    author_email="irinam.bejan@gmail.com",
    packages=find_packages(exclude=["tests"]),
    scripts=["bin/truestory"],
    include_package_data=True,
    zip_safe=False,
    install_requires=get_requirements(),
    tests_require=get_requirements("requirements-test.txt"),
    test_suite="tests",
)
