#!/usr/bin/env python3

# Always prefer setuptools over distutils
from setuptools import setup

# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="hasurino",
    version="0.1.3",
    description="Forward HFP MQTT messages into transitlog GraphQL API.",
    long_description=long_description,
    url="https://github.com/HSLdevcom/hasurino",
    author="haphut",
    author_email="haphut@gmail.com",
    license="EUPL-1.2",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="hfp mqtt graphql",
    packages=["hasurino"],
    install_requires=[
        "docopt>=0.6.0,<0.7.0",
        "paho-mqtt>=1.4.0,<2.0.0",
        "pyyaml>=3.13,<6.0",
        "requests>=2.21.0,<3.0.0",
    ],
    data_files=[("", ["LICENSE"])],
    entry_points={"console_scripts": ["hasurino=hasurino.hasurino:main"]},
)
