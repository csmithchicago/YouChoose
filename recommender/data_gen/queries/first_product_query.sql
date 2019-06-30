COPY (
    SELECT products.product_name, COUNT(p.product_id)
    FROM order_products__prior as p
    INNER JOIN orders as o
    ON o.order_id=p.order_id
    INNER JOIN products
    ON products.product_id= p.product_id
    WHERE p.add_to_cart_order=1
    GROUP BY products.product_name
    ORDER BY COUNT(p.product_id) DESC
)
TO '/home/coreys/perm-usb/coreys/Documents/instacart/analyze_instacart_data/data/processed/first_order_item_db.csv' DELIMITER ',' CSV HEADER;
