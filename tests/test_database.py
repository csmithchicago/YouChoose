# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file for full terms.
"""
Tests connections to databases.

"""
import os

# from pathlib import Path

# import numpy as np

# import paramiko
import pytest
import sqlalchemy

from youchoose.data.ingestion.sql import SQLDatabase  # , psql_engine, ssh_tunnel

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/")

# @pytest.fixture
# def postgres_db():
#     """
#     Initialise a database class connecting to a postgres database through
#     a ssh tunnel to allow for remote testing.
#     """
#     key_file = next(Path("../../").rglob("instacart_resources.pem"))
#     private_key = paramiko.RSAKey.from_private_key_file(key_file)
#     tunnel = ssh_tunnel(private_key)

#     return SQLDatabase(engine=psql_engine(tunnel=tunnel), tunnel=tunnel)


@pytest.fixture
def sqlite_db():
    """
    Initialise a database class connecting to the local sqlite test database.
    """
    return SQLDatabase(
        db_type="sqlite", db_name=f"{test_data_dir}test_instacart_database.db"
    )


def test_sqlite_table(sqlite_db):
    db_table = sqlite_db.tables["person"]
    if not isinstance(db_table, sqlalchemy.sql.schema.Table):
        raise AssertionError()


# def test_postgres_table(postgres_db):
#     db_table = postgres_db.table("orders")
#     postgres_db.close()
#     if not isinstance(db_table, sqlalchemy.sql.schema.Table):
#         raise AssertionError()


def test_incorrect_db_type():
    with pytest.raises(ValueError):
        SQLDatabase(db_type="mysql")


# def test_db_query(postgres_db):
#     query_str = "SELECT COUNT(*) FROM aisles;"
#     json_result = postgres_db.get_dataframe(query_str).to_json()
#     postgres_db.close()
#     if not json_result == '{"count":{"0":134}}':
#         raise AssertionError()

# def test_diagram_save(postgres_db):
#     test_filename = test_data_dir + "db_diagram.png"
#     postgres_db.save_layout(test_filename)
#     postgres_db.close()

#     if Path(test_filename).exists():
#         Path(test_filename).unlink()
#     else:
#         raise AssertionError()

# @pytest.fixture
# def postgres_db():  # will need a local postgres database for this test.
#     """
#     Initialise a database class connecting to a postgres database.
#     """
#     return SQLDatabase()
