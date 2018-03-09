#!/usr/bin/env python

from setuptools import setup, find_packages

desc = ''
with open('README.md') as f:
    desc = f.read()

setup(
    name='falcon-template',
    version='1.0.0',
    description=('Falcon API application template'),
    long_description=desc,
    url='https://github.com/tmeiczin/falcon_template',
    author='Terrence Meiczinger',
    author_email='terrence72@gmail.com',
    keywords='',
    packages=find_packages(exclude=['contrib', 'docs', 'test*']),
    include_package_data=True,
    install_requires=[
        'falcon>=1.1.0',
        'falcon-cors',
        'gunicorn>=19.6.0',
    ],
    package_data={'falcon_template': ['swagger/*']},
    data_files=[],
    entry_points={
        'console_scripts': [
            'falcon-app=example.__main__:main'
        ],
    },
)
