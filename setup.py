"""Setup configuration for powerbi-ontology-extractor."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="powerbi-ontology-extractor",
    version="0.1.0",
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
