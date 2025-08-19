#!/usr/bin/env python3
"""
Setup script for CodeCraft Ultimate v6.0
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text() if (this_directory / "README.md").exists() else ""

# Read requirements from requirements.txt
requirements = []
if (this_directory / "requirements.txt").exists():
    with open(this_directory / "requirements.txt") as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="codecraft-ultimate",
    version="6.0.0",
    author="CodeCraft Team",
    author_email="team@codecraft.dev",
    description="Advanced AI-Human Collaborative Development Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/codecraft/codecraft-ultimate",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Code Generators",
        "Topic :: Software Development :: Quality Assurance", 
        "Topic :: Software Development :: Testing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "codecraft=codecraft:main",
            "cc=codecraft:main",  # Short alias
        ],
    },
    include_package_data=True,
    package_data={
        "codecraft_ultimate": [
            "templates/**/*",
            "plugins/**/*", 
            "docs/**/*",
            "examples/**/*",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0", 
            "black>=23.12.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
        "ai": [
            "openai>=1.6.0",
            "anthropic>=0.8.0", 
            "transformers>=4.36.0",
        ],
        "web": [
            "fastapi>=0.108.0",
            "uvicorn>=0.25.0",
            "streamlit>=1.29.0",
        ],
        "all": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.12.0", 
            "flake8>=7.0.0",
            "mypy>=1.8.0",
            "openai>=1.6.0",
            "anthropic>=0.8.0",
            "transformers>=4.36.0", 
            "fastapi>=0.108.0",
            "uvicorn>=0.25.0",
            "streamlit>=1.29.0",
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/codecraft/codecraft-ultimate/issues",
        "Source": "https://github.com/codecraft/codecraft-ultimate",
        "Documentation": "https://codecraft-ultimate.readthedocs.io/",
    },
)