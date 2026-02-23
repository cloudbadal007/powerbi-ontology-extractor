"""Setup configuration for powerbi-ontology-extractor."""

from pathlib import Path
from setuptools import setup, find_packages

long_description = Path("README.md").read_text(encoding="utf-8")

_requirements_file = Path("requirements.txt")
if _requirements_file.exists():
    requirements = [
        line.strip()
        for line in _requirements_file.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    ]
else:
    requirements = [
        "pydantic>=2.0.0",
        "networkx>=3.0",
        "pyparsing>=3.0.0",
        "pandas>=2.0.0",
        "click>=8.0.0",
        "rich>=13.0.0",
        "matplotlib>=3.7.0",
        "plotly>=5.14.0",
        "rdflib>=6.3.0",
        "jsonschema>=4.17.0",
        "pyyaml>=6.0",
    ]

setup(
    name="powerbi-ontology-extractor",
    version="0.1.2",
    author="PowerBI Ontology Extractor Contributors",
    author_email="",
    description="Extract semantic intelligence from Power BI .pbix files and convert to formal ontologies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cloudbadal007/powerbi-ontology-extractor",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "pbi-ontology=cli.pbi_ontology_cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
