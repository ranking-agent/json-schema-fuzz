"""Set up PyPI package."""
from setuptools import find_packages, setup

setup(
    name="fuzzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "exrex>=0.10,<0.11"
    ]
)
