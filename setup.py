# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

setup(
    name='wagtail_svgmap',
    version='0.0.0',
    packages=find_packages('.', include=('wagtail_svgmap*')),
    include_package_data=True,
    install_requires=['wagtail>=1.5.3'],
    zip_safe=False,
)
