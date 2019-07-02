from setuptools import setup, find_packages

setup(
    name="youchoose",
    packages=find_packages(),
    version="0.1.0",
    description="YouChoose is an open source recommendation library built on PyTorch.",
    long_description=open("README.md").read(),
    author="Corey Smith",
    author_email="coreys@uchicago.edu",
    license="MIT",
    install_requires=["torch >= 1.1.0", "pandas >= 0.24.2"],
)
