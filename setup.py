#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name='telepath',
    version='0.1.1',
    description="A library for exchanging data between Python and JavaScript",
    author='Matthew Westcott',
    author_email='matthew.westcott@torchbox.com',
    url='https://github.com/wagtail/telepath',
    packages=["telepath"],
    include_package_data=True,
    license='BSD',
    long_description=long_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.5",
    extras_require={
        'docs': [
            'mkdocs>=1.1,<1.2',
            'mkdocs-material>=6.2,<6.3',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Framework :: Django',
    ],
)
