"""Set up PyPI package."""
from setuptools import setup, find_packages

setup(
    name="fuzzer",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "exrex>=0.10,<0.11"
    ]
)
