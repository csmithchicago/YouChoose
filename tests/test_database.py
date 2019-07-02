# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file for full terms.
"""
Tests for database class and connections.

"""
import os
import inspect
from pathlib import Path

import numpy as np
import pytest
import paramiko
import sqlalchemy

from youchoose.data_gen.database_connection import (
    Database,
    psql_database_through_tunnel,
)
from youchoose.data_gen.create_adjancency_matrix import create_adjancency_matrix

# @pytest.fixture
# def postgres_db():  # will need a local postgres database for this test.
#     """
#     Initialise a database class connecting to a postgres database.
#     """
#     return Database()

test_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/")


@pytest.fixture
def postgres_db():
    """
    Initialise a database class connecting to a postgres database through
    a ssh tunnel to allow for remote testing.
    """
    key_file = next(Path("../../").rglob("instacart_resources.pem"))
    private_key = paramiko.RSAKey.from_private_key_file(key_file)
    engine, tunnel = psql_database_through_tunnel(private_key)

    return Database(engine=engine, tunnel=tunnel)


@pytest.fixture
def sqlite_db():
    """
    Initialise a database class connecting to the local sqlite test database.
    """
    return Database(
        db_type="sqlite", db_name=f"{test_data_dir}test_instacart_database.db"
    )


def test_sqlite_table(sqlite_db):
    db_table = sqlite_db.table("person")
    if not isinstance(db_table, sqlalchemy.sql.schema.Table):
        raise AssertionError()


def test_postgres_table(postgres_db):
    db_table = postgres_db.table("orders")
    postgres_db.close()
    if not isinstance(db_table, sqlalchemy.sql.schema.Table):
        raise AssertionError()


def test_incorrect_db_type():
    with pytest.raises(ValueError):
        Database(db_type="mysql")


def test_db_query(postgres_db):
    query_str = "SELECT COUNT(*) FROM aisles;"
    json_result = postgres_db.get_dataframe(query_str).to_json()
    postgres_db.close()
    if not json_result == '{"count":{"0":134}}':
        raise AssertionError()


def test_instacart_definition(postgres_db):
    postgres_db.define_instacart_db()
    ignored_attributes = [
        "conn",
        "engine",
        "tables",
        "db_string",
        "metadata",
        "table_names",
    ]
    attributes = inspect.getmembers(postgres_db, lambda x: not (inspect.isroutine(x)))
    instacart_table_attributes = [
        a[0]
        for a in attributes
        if not (
            a[0].startswith("__") and a[0].endswith("__") or a[0] in ignored_attributes
        )
    ]
    postgres_db.close()
    if not np.all([x in instacart_table_attributes for x in postgres_db.table_names]):
        raise AssertionError()


def test_adjancency_matrix_creation(postgres_db):
    num_orders = 10
    create_adjancency_matrix(
        postgres_db, save_folder=test_data_dir, num_orders=num_orders
    )

    full_info_filename = Path(
        test_data_dir + "full_info_{}_prior_orders.csv".format(num_orders)
    )
    weighted_matrix_filename = Path(
        test_data_dir + "weighted_adjacency_matrix_{}_orders.csv".format(num_orders)
    )

    if full_info_filename.exists():
        full_info_filename.unlink()
    else:
        raise AssertionError()
    if weighted_matrix_filename.exists():
        weighted_matrix_filename.unlink()
    else:
        raise AssertionError()


def test_diagram_save(postgres_db):
    test_filename = test_data_dir + "db_diagram.png"
    postgres_db.save_layout(test_filename)
    postgres_db.close()

    if Path(test_filename).exists():
        Path(test_filename).unlink()
    else:
        raise AssertionError()
