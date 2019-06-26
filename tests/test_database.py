import os
import inspect
from pathlib import Path

import numpy as np
import pytest
import sqlalchemy

from src.data.database_connection import Database


@pytest.fixture
def postgres_db():
    """
    Initialise a database class connecting to a postgres database.

    For local tests, the database variables will need to be exported to the
    environment prior to running pytest. This can be done from the command
    line with `export $(grep -v '^#' .env | xargs)` in the same folder
    as the .env file.
    """
    return Database("", use_dotenv=False)


@pytest.fixture
def sqlite_db():
    """
    Initialise a database class connecting to the local sqlite test database.
    """
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/")
    return Database(
        "./data/.test_env",
        db_type="sqlite",
        db_name=f"{data_dir}test_instacart_database.db",
    )


def test_sqlite_table(sqlite_db):
    db_table = sqlite_db.table("person")
    assert isinstance(db_table, sqlalchemy.sql.schema.Table)


def test_postgres_table(postgres_db):
    db_table = postgres_db.table("orders")
    assert isinstance(db_table, sqlalchemy.sql.schema.Table)


def test_incorrect_db_type():
    with pytest.raises(ValueError):
        Database("", use_dotenv=False, db_type="mysql")


def test_db_query(postgres_db):
    query_str = "SELECT COUNT(*) FROM aisles;"
    json_result = postgres_db.get_dataframe(query_str).to_json()
    assert json_result == '{"count":{"0":134}}'


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

    assert np.all([x in instacart_table_attributes for x in postgres_db.table_names])


def test_diagram_save(postgres_db):
    test_filename = "db_diagram.png"
    postgres_db.save_layout(test_filename)

    assert Path(test_filename).exists()

    if Path(test_filename).exists():
        Path(test_filename).unlink()
