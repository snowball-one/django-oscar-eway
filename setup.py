#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='django-oscar-eway',
    version='versiontools:eway:',
    url='https://github.com/tangentlabs/django-oscar-eway',
    author="Sebastian Vetter",
    author_email="sebastian.vetter@tangentsnowball.com.au",
    description="eWay payment module for django-oscar (Rapid 3.0)",
    long_description=open('README.rst').read(),
    keywords="oscar,payment,django,ecommerce,eway,rapid3.0",
    license='BSD',
    packages=find_packages(exclude=['sandbox*', 'tests*']),
    install_requires=[
        'versiontools>=1.9.1',
        'django-oscar>=0.4',
        'requests>=0.13.5',
        'South>=0.7.6',
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
