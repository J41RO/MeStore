#!/usr/bin/env python3
"""
Surgical Modifier v6.0 - Setup for global installation
The most complete code modification tool in the world
"""

import os
import sys

# Verificar Python version
if sys.version_info < (3, 8):
    sys.exit("Python 3.8 or higher is required.")

# Read long description safely
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "The most complete code modification tool in the world"

# Read requirements safely  
def read_requirements(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f 
                   if line.strip() and not line.startswith("#")]
    except FileNotFoundError:
        return []

# Import setuptools after functions
try:
    from setuptools import setup, find_packages
except ImportError:
    sys.exit("setuptools is required. Install with: pip install setuptools")

setup(
    name="surgical-modifier",
    version="6.0.0",
    description="The most complete code modification tool in the world",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Surgical Modifier Team",
    author_email="team@surgicalmodifier.dev",
    url="https://github.com/surgical-modifier/surgical-modifier",
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=read_requirements("requirements.txt"),
    extras_require={
        "future": read_requirements("requirements-future.txt"),
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0", 
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "made=surgical_modifier.__main__:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9", 
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="code modification surgical programming development tools",
    zip_safe=False,
)
