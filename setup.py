#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = [ 'pandas', 'pint', 'tabulate', 'feelpp', 'feelpp-toolboxes', 'feelpp-toolboxes-core', 'feelpp-toolboxes-coefficientformpdes', ]

setup_requirements = [ ]

test_requirements = ['pytest>=3', ]

setup(
    author="Christophe Trophime",
    author_email='christophe.trophime@lncmi.cnrs.fr',
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="Python Magnet Workflows",
    entry_points={
        'console_scripts': [
            'python_magnetworkflows=python_magnetworkflows.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='python__magnetworkflows',
    name='python_magnetworkflows',
    packages=find_packages(include=['python_magnetworkflows', 'python_magnetworkflows.*']),
    package_data={'': []},
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/Trophime/python_magnetworkflows',
    version='0.1.0',
    zip_safe=False,
)
