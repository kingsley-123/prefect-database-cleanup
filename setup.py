"""
Setup configuration for Prefect Database Cleanup

Enterprise-grade database maintenance toolkit for Prefect deployments.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Read requirements
requirements = []
with open('requirements.txt', 'r', encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="prefect-database-cleanup",
    version="1.0.0",
    author="Kingsley",
    author_email="kingsley.prefect@gmail.com",
    description="Enterprise-grade database cleanup toolkit for Prefect deployments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kingsley-123/prefect-database-cleanup",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Framework :: Prefect",
    ],
    keywords=[
        "prefect", 
        "database", 
        "cleanup", 
        "maintenance", 
        "retention", 
        "backup",
        "enterprise",
        "workflow",
        "orchestration",
        "data-engineering"
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
        "postgresql": [
            "psycopg2-binary>=2.9.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "prefect-cleanup=prefect_cleanup.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "prefect_cleanup": ["*.py"],
    },
    project_urls={
        "Bug Reports": "https://github.com/kingsley-123/prefect-database-cleanup/issues",
        "Source": "https://github.com/kingsley-123/prefect-database-cleanup",
        "Documentation": "https://github.com/kingsley-123/prefect-database-cleanup#readme",
    },
    zip_safe=False,
)