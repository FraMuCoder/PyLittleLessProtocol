# Little Less Protocol for Python
#
# Copyright (C) 2021 Frank Mueller
#
# SPDX-License-Identifier: MIT

import setuptools

with open('README.md', 'r', encoding='utf-8') as readme:
    long_description = readme.read()

setuptools.setup(
    name='littlelessprotocol',
    version='0.0.1',
    author='Frank Müller',
    description='Python implementation for the simple serial protocol "Little Less Protocol".',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/FraMuCoder/PyLittleLessProtocol',
    packages=setuptools.find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Communications',
        'Topic :: Terminals :: Serial',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
    install_requires=['pyserial'],
)