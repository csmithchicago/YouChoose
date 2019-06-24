Analyze Instacart Data
==============================

[![Build Status](https://travis-ci.org/csmithchicago/analyze_instacart_data.svg?branch=master)](https://travis-ci.org/csmithchicago/analyze_instacart_data)

[![Coverage Status](https://coveralls.io/repos/github/csmithchicago/analyze_instacart_data/badge.svg?branch=master)](https://coveralls.io/github/csmithchicago/analyze_instacart_data?branch=master)

Project Overview
------------

In this project I seek to analyze transaction data released by Instacart in 2017 as part of a [Kaggle competition](https://www.kaggle.com/c/instacart-market-basket-analysis/overview). The following is directly from the competition overview.

> Instacart’s data science team plays a big part in providing this delightful shopping experience. Currently they use transactional data to develop models that predict which products a user will buy again, try for the first time, or add to their cart next during a session. Recently, Instacart open sourced this data - see their blog post on [3 Million Instacart Orders, Open Sourced](https://tech.instacart.com/3-million-instacart-orders-open-sourced-d40d29ead6f2).
>In this competition, Instacart is challenging the Kaggle community to use this anonymized data on customer orders over time to predict which previously purchased products will be in a user’s next order. 

Submissions are evaluated based on the mean F1 score. The format of submissions need to follow the following format.

>For each order_id in the test set, you should predict a space-delimited list of product_ids for that order. If you wish to predict an empty order, you should submit an explicit 'None' value. You may combine 'None' with product_ids. The spelling of 'None' is case sensitive in the scoring metric. The file should have a header and look like the following:
>
>
><p style="text-align: center;">order_id,products<br/>17,1 2 <br/>34,None<br/>137,1 2 3</p>

Project Set-Up
------------

### Virtual Environment and Clone Repository

The best way to run the code is to use a python virtual environment. This will require that you have python3 and git already installed on your system. To begin, run `python3 -m venv project-name` to create a virtual environment in a folder called project-name. Now run `cd project-name` to change directories. The following command is then run to clone the repository.
`git clone https://github.com/csmithchicago/analyze_instacart_data.git`

### Install Python Requirements

`source bin/activate`
`cd analyze_instacart_data`
`pip install -r requirements.txt`

### Data Download

The transaction data can be downloaded in a zip file from Instacart at the following [link](https://www.instacart.com/datasets/grocery-shopping-2017). After downloading the unzipped data should be placed in `./data/external/`.

This can also be done by running `python ./src/data/get_instacart_data.py` from the command line. This will download the files and place them in the correct folder.

Project Organization
------------

    ├── LICENSE
    ├── Makefile           <- Makefile with commands like `make data` or `make train`
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources.
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    │
    ├── models             <- Trained and serialized models, model predictions, or model summaries
    │
    ├── notebooks          <- Jupyter notebooks. Naming convention is a number (for ordering),
    │                         and a short `-` delimited description, e.g.
    │                         `1.0-initial-data-exploration`.
    │
    ├── references         <- Data dictionaries, manuals, and all other explanatory materials.
    │
    ├── reports            <- Generated analysis as HTML, PDF, LaTeX, etc.
    │   └── figures        <- Generated graphics and figures to be used in reporting
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │
    │   ├── data           <- Scripts to download or generate data
    │   │   ├── queries    <- SQL queries for database creation and querying
    │   │   └── make_dataset.py
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   └── build_features.py
    │   │
    │   ├── models         <- Scripts to train models and then use trained models to make
    │   │   │                 predictions
    │   │   ├── predict_model.py
    │   │   └── train_model.py
    │   │
    │   └── visualization  <- Scripts to create exploratory and results oriented visualizations
    │       └── visualize.py
    │
    ├── tests             <- Tests to check functionality of codebase
    │
    └── tox.ini            <- tox file with settings for running tox; see tox.testrun.org

--------

Project References
------------

* "The Instacart Online Grocery Shopping Dataset 2017", Accessed from [Instacart](https://www.instacart.com/datasets/grocery-shopping-2017) on 06-16-2019* Project based on the cookiecutter data science project [template](https://drivendata.github.io/cookiecutter-data-science/).