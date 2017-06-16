import os
import re

from setuptools import setup
from setuptools import find_packages


here = os.path.abspath(os.path.dirname(__file__))

def get_version(*file_paths):
    """Retrieves the version from anno/__init__.py"""
    filename = os.path.join(here, *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("catchpy_functests", "__init__.py")

# Get the long description from the README file
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# get the dependencies and installs
with open(os.path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')

install_requires = [x.strip() for x in all_reqs if 'git+' not in x]
dependency_links = [x.strip().replace('git+', '') for x in all_reqs if x.startswith('git+')]

setup(
    name='catchpy_functests',
    version=version,
    description='functional tests for catchpy',
    long_description=long_description,
    url='https://github.com/nmaekawa/catchpy_functests',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    author='nmaekawa',
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email='nmaekawa@g.harvard.edu',
    zip_safe=False,
)
