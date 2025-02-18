from setuptools import setup, find_packages

setup(
    name="dibkb_scraper",
    version="0.1.4",
    packages=find_packages(),
    install_requires=[
        "httpx",
        "beautifulsoup4",
        "bs4",
        "pydantic",
    ],
    author="Dibas K Borborah",
    author_email="dibas9110@gmail.com",
    description="A scraper for Amazon product details using ASIN",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/dibkb/dibkb_scraper",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
