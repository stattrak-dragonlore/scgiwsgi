#!/usr/bin/env python
from setuptools import setup

setup(
    name = "scgiwsgi",
    version = "0.1",
    py_modules = ["scgiwsgi"],
    author = "Deng Zhiping",
    author_email = "kofreestyler@gmail.com",
    install_requires = ['scgi>=1.14'],
    url = "https://github.com/dengzhp/scgiwsgi",
    description = "a WSGI server based on scgi_server",
)
