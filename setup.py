#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

from eway import get_version


setup(
    name='django-oscar-eway',
    version=get_version(),
    url='https://github.com/tangentlabs/django-oscar-eway',
    author="Sebastian Vetter",
    author_email="sebastian.vetter@tangentsnowball.com.au",
    description="eWay payment module for django-oscar (Rapid 3.0)",
    long_description='\n\n'.join([
        open('README.rst').read(),
        open('CHANGELOG.rst').read(),
    ]),
    keywords="oscar,payment,django,ecommerce,eway,rapid3.0",
    license='BSD',
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    install_requires=[
        'django-oscar>=0.4',
        'requests>=1.0',
    ],
    include_package_data=True,
    # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python'
    ]
)
