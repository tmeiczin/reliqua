#!/usr/bin/env python

from setuptools import setup, find_packages

desc = ''
with open('README.md') as f:
    desc = f.read()

setup(
    name='unrest',
    version='1.0.0',
    description=('API application template'),
    long_description=desc,
    url='https://github.com/tmeiczin/falcon_template',
    author='Terrence Meiczinger',
    author_email='terrence72@gmail.com',
    keywords='',
    packages=find_packages('src'),
    package_dir ={'': 'src'},
    include_package_data=False,
    install_requires=[
        'falcon>=1.4.0',
        'falcon-cors',
        'gunicorn>=19.6.0',
        'six',
    ],
    package_data={'unrest': ['swagger/*']},
    data_files=[],
    entry_points={
        'console_scripts': [
            'unrest-example=unrest.example.__main__:main'
        ],
    },
)
