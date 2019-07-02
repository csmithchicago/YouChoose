# # Copyright (c) 2019, Corey Smith
# # Distributed under the MIT License.
# # See LICENCE file for full terms.
# """
# Tests for the data examples.

# """
# # import sys
# import inspect

# # import os
# from pathlib import Path

# import numpy as np

# # import paramiko
# # import pytest
# # import sqlalchemy

# # sys.path.append(("../"))
# # from ingestion.sql import SQLDatabase, psql_engine
# # from ingestion.helper_functions import ssh_tunnel
# from instacart_dataset import create_adjancency_matrix


# def test_instacart_definition(postgres_db):
#     postgres_db.define_instacart_db()
#     ignored_attributes = [
#         "conn",
#         "engine",
#         "tables",
#         "db_string",
#         "metadata",
#         "table_names",
#     ]
#     attributes = inspect.getmembers(postgres_db, lambda x: not (inspect.isroutine(x)))
#     instacart_table_attributes = [
#         a[0]
#         for a in attributes
#         if not (
#             a[0].startswith("__") and a[0].endswith("__") or a[0] in ignored_attributes
#         )
#     ]
#     postgres_db.close()
#     if not np.all([x in instacart_table_attributes for x in postgres_db.table_names]):
#         raise AssertionError()


# def test_adjancency_matrix_creation(postgres_db, test_data_dir=""):
#     num_orders = 10
#     create_adjancency_matrix(
#         postgres_db, save_folder=test_data_dir, num_orders=num_orders
#     )

#     full_info_filename = Path(
#         test_data_dir + "full_info_{}_prior_orders.csv".format(num_orders)
#     )
#     weighted_matrix_filename = Path(
#         test_data_dir + "weighted_adjacency_matrix_{}_orders.csv".format(num_orders)
#     )

#     if full_info_filename.exists():
#         full_info_filename.unlink()
#     else:
#         raise AssertionError()
#     if weighted_matrix_filename.exists():
#         weighted_matrix_filename.unlink()
#     else:
#         raise AssertionError()
