# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Create connections to a postgres database either locally or remotly
using python's sqlalchemy.

"""
import os
import urllib.parse

import pandas as pd
import sshtunnel
from dotenv import find_dotenv, load_dotenv

from eralchemy import render_er
from sqlalchemy import MetaData, create_engine


class Database:
    """
    Database is a class used to connect to a relational database using sqlalchemy
    and an env file containing the database credentials.

    Some more info about the class attributes and functions.
    """

    def __init__(self, db_type="psql", db_name="", engine=None, tunnel=None):
        """
        Initialize the database class with the path to the env file containing
        the database credentials.

        Args:
            engine (sqlalchemy engine): Giving an engine object allows for a
                ssh tunnel to be set-up and to connect the database through it.
        """

        if db_type == "psql" and engine is None:
            engine = psql_engine()

        elif db_type == "sqlite" and engine is None:
            engine = create_engine("sqlite:///{}".format(db_name))

        if engine is None:
            raise ValueError(
                "Database type must be postgres or sqlite if no engine is given."
            )

        self.tunnel = tunnel
        self.engine = engine
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
        render_er(self.metadata, filename)

    def close(self):
        """Shutdown database connection and ssh tunnel if open."""
        self.conn.close()
        self.engine.dispose()

        if self.tunnel is not None:
            self.tunnel.stop()
            self.tunnel.close()


def get_env_parameters():
    """
    Load in environment variables for database and ssh connections.

    Return:
        env_dict: A dictionary of the variables needed for ssh and database
            connections.
    """
    _ = load_dotenv(find_dotenv())  # evaluates to True

    env_dict = {
        "HOST_IP": os.getenv("HOST_IP", ""),
        "HOST_USER": os.getenv("HOST_USER", ""),
        "SSH_PORT": int(os.getenv("SSH_PORT", 22)),
        "DB_PORT": int(os.getenv("DB_PORT", 5432)),
        "DB_NAME": os.getenv("DB_NAME"),
        "DB_USER": os.getenv("DB_USER", "postgres"),
        "DB_PASSWORD": urllib.parse.quote_plus(os.getenv("DB_PASSWORD", "")),
        "DB_HOST": os.getenv("DB_HOST"),
    }

    return env_dict


def psql_database_through_tunnel(private_key):
    """
    Connect to a postgres database through a ssh tunnel.

    Use to connect to a database that is not accessible through a
    public ip address.
    Args:
        private_key (RSA key): RSA key used to connect with host computer.
        HOST_IP (IP address): IP for the host to tunnel to.
        SSH_PORT (int): Open port on host to ssh through.
        HOST_USER (str): Username on host computer.
        DB_HOST: Hostname/endpoint of the postgres database.
        DB_PORT (int): Open port on database for connection.
        DB_USER: Username for the database.
        DB_PASSWORD: Password for the database user.
        DB_NAME: Name of the database to connect to.
    Return:
        engine (sqlalchmey engine): A sqlalchmey engine used to create the
            database connection.
    """
    sshtunnel.SSH_TIMEOUT = 30.0
    sshtunnel.TUNNEL_TIMEOUT = 30.0

    ssh_db_dict = get_env_parameters()

    tunnel = sshtunnel.SSHTunnelForwarder(
        (ssh_db_dict.get("HOST_IP"), ssh_db_dict.get("SSH_PORT")),
        ssh_username=ssh_db_dict.get("HOST_USER"),
        ssh_pkey=private_key,
        remote_bind_address=(ssh_db_dict.get("DB_HOST"), ssh_db_dict.get("DB_PORT")),
    )
    tunnel.start()

    return psql_engine(tunnel=tunnel), tunnel


def psql_engine(tunnel=None):
    """
    Create a sqlalchmey engine used for creating the
    database connection.
    """
    env_dict = get_env_parameters()

    if tunnel is not None:
        db_conn = "localhost:{}".format(tunnel.local_bind_port)
    else:
        db_conn = env_dict.get("DB_HOST")

    db_user = "postgresql+psycopg2://{}:{}@".format(
        env_dict.get("DB_USER"), env_dict.get("DB_PASSWORD")
    )
    db_name = "/{}".format(env_dict.get("DB_NAME"))

    db_string = db_user + db_conn + db_name

    return create_engine(db_string)
