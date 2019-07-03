from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires = [
    "matplotlib",
    "numpy",
    "pandas>=0.24.2",
    "scikit-learn",
    "sklearn",
    "torch>=1.1.0",
    "torchvision",
    "tqdm",
]


def get_requirements(env):
    with open(u"requirements{}.txt".format(env)) as fp:
        return [x.strip() for x in fp.read().split("\n") if not x.startswith("#")]


dev_requires = get_requirements("")

# tests_require = get_requirements('test')

setup(
    name="youchoose",
    packages=find_packages(),
    version="0.1.2",
    description="YouChoose is an open source recommendation library built on PyTorch.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Corey Smith",
    author_email="coreys@uchicago.edu",
    url="https://github.com/csmithchicago/YouChoose",
    license="MIT",
    install_requires=install_requires,
    extras_require={
        "dev": dev_requires,
        # 'postgres': [],
        # 'tests': tests_require,
        # 'optional': optional_requires,
    },
)
