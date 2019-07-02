# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Download and unzip instacart data.

"""
import os
import shutil
from datetime import datetime

import wget
import requests
from bs4 import BeautifulSoup


def create_adjancency_matrix(db, save_folder="../../data/interim/", num_orders=10):
    """
    Create and save a weighted adjacency matrix of the instacart database.

    Args:
        db (Database): The connected instacart database.
        save_folder (str, optional): File location to save the data to. Defaults
            to "../../data/interim/".
        num_orders (int, optional): The number of orders to get interactions from.
            Defaults to 10.

    Raises:
        TypeError: If the number of orders is not an int.
    """
    if not isinstance(num_orders, int):
        raise TypeError("Number of orders must be of type int.")

    query_string = """
        SELECT
            CAST (o.user_id AS INTEGER),
            p.product_id,
            COUNT(p.product_id) AS weight
        FROM
            order_products__prior as p
        INNER JOIN
            (
                SELECT
                    order_id,
                    user_id
                FROM
                    orders
                WHERE
                    eval_set='prior'
                LIMIT
                    {}
            ) AS o
        ON
            o.order_id=p.order_id
        GROUP BY
            o.user_id, p.product_id
        ;
        """.format(
        num_orders
    )
    df = db.get_dataframe(query_string)
    df.to_csv(
        save_folder + "weighted_adjacency_matrix_{}_orders.csv".format(num_orders),
        index=False,
    )

    # Ouery the database to create a table of 10,000 prior orders to use for prototyping functions.
    prior_orders_query = """
        SELECT
            o.user_id, p.product_id,
            products.department_id, products.aisle_id,
            p.order_id, p.add_to_cart_order,
            p.reordered, o.order_number,
            o.order_dow, o.order_hour_of_day,
            CAST (o.days_since_prior AS INTEGER)
        FROM
            order_products__prior AS p
        INNER JOIN
        (
            SELECT
                user_id, order_id, order_number,
                order_dow, order_hour_of_day,
                days_since_prior
            FROM
                orders
            WHERE
                order_id IN
                (
                    SELECT
                        DISTINCT order_id
                    FROM
                        orders
                    WHERE
                        eval_set='prior'
                    LIMIT
                        {}
                )
        ) AS o
        ON
            o.order_id=p.order_id
        INNER JOIN
            products
        ON
            products.product_id=p.product_id
        ;
    """.format(
        num_orders
    )

    df = db.get_dataframe(prior_orders_query)
    df.to_csv(
        save_folder + "full_info_{}_prior_orders.csv".format(num_orders), index=False
    )
    db.close()


def define_instacart_db(db):
    """
    Add the instacart database tables as attributes of the Database class.
    """
    db.departments = db.tables["departments"]
    db.orders = db.tables["orders"]
    db.aisles = db.tables["aisles"]
    db.order_products__prior = db.tables["order_products__prior"]
    db.products = db.tables["products"]
    db.order_products__train = db.tables["order_products__train"]
    db.orders_test = db.tables["orders_test"]
    db.orders_no_tests = db.tables["orders_no_tests"]


def main():
    project_dir = os.path.join(os.path.dirname(__file__), os.pardir)
    data_path = os.path.join(project_dir, "../data/")
    extract_dir = data_path + "external/"
    page_url = "https://www.instacart.com/datasets/grocery-shopping-2017"

    # only download files in the extracted directory doesn't exist.
    if not os.path.isdir(extract_dir + "instacart_2017_05_01/"):
        print("Getting files ...")

        download_zip_filename = data_path + "instacart_data.tar.gz"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (X11; Linux x86_64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/73.0.3683.86 Safari/537.36"
            )
        }
        try:
            data = requests.get(page_url, headers=headers)
            data.raise_for_status()
        except Exception as e:
            print(
                f"Error: {e}. Unable to fetch URL for dataset. "
                f"Please visit [{page_url}] to download the dataset."
            )

        instacart_html = BeautifulSoup(data.content, "html.parser")

        for anchor in instacart_html.select("a"):
            if anchor["href"].startswith("https://s3"):
                data_url = anchor["href"]

        print("Beginning file download ...")
        wget.download(data_url, download_zip_filename)

        print("\nUnzipping csv files ...")
        shutil.unpack_archive(download_zip_filename, extract_dir)
        os.remove(download_zip_filename)

    print("Add data attribution to README file ...")
    with open(project_dir + "/../README.md", "r") as f:
        content = f.readlines()

    attribution = (
        f'"The Instacart Online Grocery Shopping Dataset 2017", '
        f"Accessed from [Instacart]({page_url}) "
        f"on {datetime.now():%m-%d-%Y}"
    )

    for idx, line in enumerate(content):
        if repr(line) == repr("Project References\n"):
            ref_line = idx
            break

    first_item = ref_line + 3
    check_for = "The Instacart Online Grocery Shopping Dataset 2017"
    attribution_line = "* " + attribution

    # Is data attribution the first bullet item in references?
    if not content[first_item].startswith(check_for, 3):
        content.insert(first_item, "\n")
        content.insert(first_item, "\n")
        content.insert(first_item, attribution_line)
    # Check to make sure date is current to today.
    elif content[first_item] != attribution_line:
        content[first_item] = attribution_line

    with open("README.md", "w") as f:
        for line in content:
            f.write(line)


if __name__ == "__main__":
    main()

    # from .ingestion.sql import SQLDatabase
    # create_adjancency_matrix(SQLDatabase())
