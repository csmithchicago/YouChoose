import os

import pytest
import sqlalchemy

from src.data.database_connection import Database


@pytest.fixture
def db_connection():
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data/")
    return Database(
        "./data/.test_env",
        db_type="sqlite",
        db_name=f"{data_dir}test_instacart_database.db",
    )


def test_database_table(db_connection):
    db_table = db_connection.table("person")
    assert type(db_table) == sqlalchemy.sql.schema.Table
