#!/usr/bin/python3

import setuptools
import ascii_progress


with open("README.md", "r") as fd:
    long_description = fd.read()

setuptools.setup(
    name="ascii-progress",
    license="LICENSE",
    version=ascii_progress.__version__,
    author=ascii_progress.__author__,
    author_email=ascii_progress.__email__,
    description=ascii_progress.__doc__,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=ascii_progress.__contact__,
    packages=["ascii_progress"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.0',
)
