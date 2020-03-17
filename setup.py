#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import bucketcloner

setup(
    name='bucketcloner',

    version='2.0.0',
    packages=find_packages(),
    author="Léo Depriester",
    author_email="leo.depriester@camptocamp.com",
    entry_points = {
        'console_scripts': [
            'bkc = bucketcloner.core:main',
        ],
    },
    license="Apache 2",
)
