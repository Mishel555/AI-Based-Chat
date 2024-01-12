from pathlib import Path

from setuptools import find_packages, setup

with open(Path(__file__).absolute().parent.joinpath('requirements.txt')) as f:
    requirements = f.read().splitlines()

setup(
    name='vector_store_faissdb',
    version='0.1',
    packages=find_packages(),
    install_requires=requirements,
)
