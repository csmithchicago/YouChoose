# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Library of functions used to connect and query a SQL database. Connections can be
either local or remote and are connected using using SQLAlchemy. A SSH tunnel can
be set-up if the remote database is not directly accessable.
"""
import pandas as pd
from sqlalchemy import MetaData, create_engine

# from sqlalchemy.engine.base import Engine


class SQLDatabase:
    """
    SQLDatabase is a class used to connect to a relational database using sqlalchemy
    and an env file containing the database credentials.

    Some more info about the class attributes and functions.
    """

    def __init__(self, db_type="psql", db_name="", engine=None, tunnel=None):
        """
        Initialize the database class with the path to the env file containing
        the database credentials

        [extended_summary]

        Args:
            db_type (str, optional): Type of SQL database. Defaults to "psql".
            db_name (str, optional): The name of the database. Defaults to "".
            engine (Engine, optional): Giving an engine object allows for a
                ssh tunnel to be set-up and to connect the database through it.
                Defaults to None.
            tunnel (sshtunnel.SSHTunnelForwarder, optional): The ssh tunnel
                through which to connect to the database. Defaults to None.

        Raises:
            ValueError: If the connection type provided is not a psql or sqlite
                database.
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

    def get_dataframe(self, query: str) -> pd.DataFrame:
        """
        Execute the query on the connected database and return a pandas dataframe.

        Args:
            query (str): SQL query

        Returns:
            queried_df (pd.DataFrame): Results of the sql query returned as a dataframe
                with headings included.
        """
        result_proxy = self.conn.execute(query)
        headings = result_proxy.keys()
        data = []
        for row in result_proxy:
            data.append(row.values())

        queried_df = pd.DataFrame(data, columns=headings)

        return queried_df

    def save_layout(self, filename: str):
        """
        Save the layout of the database to file.

        Args:
            filename (str): Filetypes are png, dot, er (markdown), and pdf.
        """
        from eralchemy import render_er

        render_er(self.metadata, filename)

    def close(self):
        """Shutdown database connection and ssh tunnel if open."""
        self.conn.close()
        self.engine.dispose()

        if self.tunnel is not None:
            self.tunnel.stop()
            self.tunnel.close()


def psql_engine(tunnel=None):
    """
    Create a sqlalchmey engine used for creating the database connection.

    Args:
        tunnel (sshtunnel.SSHTunnelForwarder, optional): Connect using an opened ssh
            tunnel if needed. Defaults to None.

    Returns:
        Engine: The SQLAlchemy engine used to create the database connection.
    """
    import helper_functions

    env_dict = helper_functions.get_env_parameters()

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
