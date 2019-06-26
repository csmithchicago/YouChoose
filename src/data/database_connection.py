"""
Create connections to a postgres database either locally or remotly
using python's sqlalchemy.


Copyright (c) 2019, Corey Smith
Distributed under the MIT License.
See LICENCE file for full terms.
"""
import os
import urllib.parse

import dotenv
import pandas as pd
from eralchemy import render_er
from sqlalchemy import MetaData, create_engine


class Database:
    """
    Database is a class used to connect to a relational database using sqlalchemy
    and an env file containing the database credentials.

    Some more info about the class attributes and functions.
    """

    def __init__(self, dotenv_path, db_type="psql", db_name="", use_dotenv=True):
        """
        Initialize the database class with the path to the env file containing
        the database credentials.
        """
        if use_dotenv:
            _ = dotenv.load_dotenv(dotenv_path=dotenv_path)

        DB_PASSWORD = os.getenv("DB_PASSWORD", "")
        DB_NAME = os.getenv("DB_NAME")
        DB_USER = os.getenv("DB_USER", "postgres")
        DB_HOST = os.getenv("DB_HOST", "")

        if db_type == "psql":
            self.db_string = (
                f"postgresql+psycopg2://{DB_USER}:"
                f"{urllib.parse.quote_plus(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}"
            )
        elif db_type == "sqlite":
            self.db_string = f"sqlite:///{db_name}"
        else:
            raise ValueError("Database must be a postgres or sqlite database.")

        self.engine = create_engine(self.db_string)
        self.conn = self.engine.connect()

        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)

        self.tables = self.metadata.tables
        self.table_names = self.tables.keys()

    def table(self, table_name: str):
        """
        Get a specific table object from the database.
        """
        return self.tables[table_name]

    def get_dataframe(self, query):
        """
        Execute the query and return a pandas dataframe.
        """
        result_proxy = self.conn.execute(query)
        headings = result_proxy.keys()
        data = []
        for row in result_proxy:
            data.append(row.values())

        return pd.DataFrame(data, columns=headings)

    def define_instacart_db(self):
        """
        Add the instacart database tables as attributes of the Database class.
        """
        self.departments = self.tables["departments"]
        self.orders = self.tables["orders"]
        self.aisles = self.tables["aisles"]
        self.order_products__prior = self.tables["order_products__prior"]
        self.products = self.tables["products"]
        self.order_products__train = self.tables["order_products__train"]
        self.orders_test = self.tables["orders_test"]
        self.orders_no_tests = self.tables["orders_no_tests"]

    def save_layout(self, filename):
        """
        Save the layout of the database to file.

        Allowed filetypes are png, dot, er (markdown), and pdf.
        """
        render_er(self.db_string, filename)
