# -*- coding: utf-8 -*-
from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='tangent-tokenauth',
    version='0.1.0',
    author=u'Tangent Solutions',
    author_email=u'admin@tangentsolutions.co.za',
    packages=['tokenauth'],
    include_package_data=True,
    install_requires=required,
    url='https://github.com/TangentMicroServices/PythonAuthenticationLib',
    license='MIT licence, see LICENCE',
    description='Authentication lib for Tangent Micro Services',
    long_description=open('README.md').read(),
)
