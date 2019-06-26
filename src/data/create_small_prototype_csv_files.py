"""
Create two small prototype csv files for use when creating
and testing analysis and visualization functions.

Copyright (c) 2019, Corey Smith
Distributed under the MIT License.
See LICENCE file for full terms.
"""

import os

from database_connection import Database

project_dir = os.path.join(os.path.dirname("__file__"), os.pardir)
dotenv_path = os.path.join("../" + project_dir, ".env")

db = Database(dotenv_path)

# Make weighted adjacency matrix from the instacart database
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
                10000
        ) AS o
    ON
        o.order_id=p.order_id
    GROUP BY
        o.user_id, p.product_id
    ;
    """
df = db.get_dataframe(query_string)
df.to_csv(
    "../../data/interim/small_10000_orders_weighted_adjacency_matrix.csv", index=False
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
                    10000
            )
    ) AS o
    ON
        o.order_id=p.order_id
    INNER JOIN
        products
    ON
        products.product_id=p.product_id
    ;
"""

df = db.get_dataframe(prior_orders_query)
df.to_csv("../../data/interim/prior_10000_orders_full_info.csv", index=False)
