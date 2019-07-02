# YouChoose

[![Build Status](https://travis-ci.org/csmithchicago/YouChoose.svg?branch=master)](https://travis-ci.org/csmithchicago/YouChoose)
[![Coverage Status](https://coveralls.io/repos/github/csmithchicago/YouChoose/badge.svg)](https://coveralls.io/github/csmithchicago/YouChoose)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/413dbdc41b89490da86758b6dc980d3c)](https://www.codacy.com/app/csmithchicago/YouChoose?utm_source=github.com&utm_medium=referral&utm_content=csmithchicago/YouChoose&utm_campaign=Badge_Grade)
[![Documentation Status](https://readthedocs.org/projects/youchoose/badge/?version=latest)](https://youchoose.readthedocs.io/en/latest/?badge=latest)

## Project Overview

A recommender system built on PyTorch. I wanted a library similar to what was provided
in OpenRec but for PyTorch. Spotlight is a similar package but appears to have died. And
while it does have some nice features, instead of forking it and building on it,
I wanted to start at the ground floor to build a library that would be simple to use but
also easy to configure.

## Project Set-Up

### Virtual Environment

The best way to run the code is to use a python virtual environment. This will require that you have python3 and git already installed on your system. To begin, run `python3 -m venv project-name` to create a virtual environment in a folder called project-name. Now run `cd project-name` to change directories.

### Install with PIP

```sh
pip install youchoose
```

### Install From Source

The following command is then run to clone the repository.

```sh
git clone https://github.com/csmithchicago/YouChoose.git

source bin/activate
cd youchoose
pip install -r requirements.txt
```

## Project References

