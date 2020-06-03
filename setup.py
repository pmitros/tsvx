"""Setup for tsvx, an extended TSV format."""

import os
from setuptools import setup


setup(
    name='tsvx',
    version='0.00001',
    description='Prototype package for TSVx files',
    packages=[
        'tsvx'
    ],
    scripts=[
        'scripts/tsv2tsvx.py'
    ],
    install_requires=[
        'python-dateutil',
        'docopt',
        'pyyaml'
    ]
)
