#!/usr/bin/env python
from os import path
from setuptools import setup


with open(path.join(path.dirname(__file__), "README.rst")) as f:
    readme = f.read()

setup(
    name="cqstat",
    version="1.0.0",
    description="A colorful command line tool substitutes for Grid Engine qstat command",
    long_description=readme,
    url="https://github.com/ronin-gw/cqstat",
    download_url="https://github.com/ronin-gw/cqstat",
    author="Hayato Anzawa",
    author_email="andy@a-fal.com",
    license="MIT",
    platforms=["POSIX", "Mac OS X"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Topic :: Utilities"
    ],
    keywords="GridEngine",
    packages=["cqstat"],
    entry_points={
        "console_scripts": ["cqstat = cqstat.__main__:main"]
    }
)
