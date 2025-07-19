from setuptools import setup

setup(
    name="wiki-search",
    version="1.0",
    packages=["src"],
    install_requires=[
        "PyQt6",
        "requests"
    ],
    entry_points={
        "console_scripts": [
            "wiki-search=src.app:main",
        ],
    },
)