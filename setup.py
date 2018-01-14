import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="iota_faucet",
    version="0.0.1",
    author="eukaryote",
    description="An IOTA Faucet.",

    license="MIT",
    keywords="iota,faucet,cryptocurrency",
    url="",
    packages=find_packages('.', exclude=('test', 'test.*')),
    long_description=read('README.md'),
    install_requires=[
        'records==0.5.2',
        'pyota==2.0.3',
        'mysqlclient==1.3.12'
    ]
)
