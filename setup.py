from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="youchoose",
    packages=find_packages(),
    version="0.1.0",
    description="YouChoose is an open source recommendation library built on PyTorch.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Corey Smith",
    author_email="coreys@uchicago.edu",
    url="https://github.com/csmithchicago/YouChoose",
    license="MIT",
    install_requires=["torch >= 1.1.0", "pandas >= 0.24.2"],
)
