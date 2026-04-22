#!/usr/bin/env python3
"""
Setup script for OpenIssue CLI
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent.parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "requests>=2.28.0",
    "google-generativeai>=0.3.0",
]

setup(
    name="openissue-cli",
    version="1.0.0",
    description="AI-powered security vulnerability scanner with GitHub integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="OpenIssue Team",
    author_email="team@openissue.dev",
    url="https://github.com/yourusername/openissue",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "openissue=openissue.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=3.8",
    keywords="security vulnerability scanner ci cd github sarif",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/openissue/issues",
        "Source": "https://github.com/yourusername/openissue",
        "Documentation": "https://github.com/yourusername/openissue/docs",
    },
)