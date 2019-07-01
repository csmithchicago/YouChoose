# Copyright (c) 2019, Corey Smith
# Distributed under the MIT License.
# See LICENCE file in root directory for full terms.
"""
Create two small prototype csv files for use when creating
and testing analysis and visualization functions.

"""


def create_adjancency_matrix(db, save_folder="../../data/interim/", num_orders=10):
    """
    Make weighted adjacency matrix from the instacart database.
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


if __name__ == "__main__":
    from .database_connection import Database

    create_adjancency_matrix(Database())
