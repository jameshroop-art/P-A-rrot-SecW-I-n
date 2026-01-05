from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="forensicsense",
    version="1.0.0",
    author="James Hroop",
    author_email="",
    description="ForensicSense AI - Forensics-first Penetration Testing Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jameshroop-art/P-A-rrot-SecW-I-n",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "aiohttp>=3.9.0",
        "dnspython>=2.4.0",
        "requests>=2.31.0",
        "python-nmap>=0.7.1",
        "shodan>=1.30.0",
        "pyyaml>=6.0",
        "reportlab>=4.0.0",
        "jinja2>=3.1.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "python-whois>=0.8.0",
        "cryptography>=41.0.0",
        "pyjwt>=2.8.0",
        "click>=8.1.0",
        "rich>=13.7.0",
        "tabulate>=0.9.0",
        "colorama>=0.4.6",
    ],
    entry_points={
        "console_scripts": [
            "forensicsense=forensicsense.cli.main:main",
        ],
    },
)
