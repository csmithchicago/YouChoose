COPY public.order_products__prior (order_id, product_id, add_to_cart_order, reordered)
FROM '/home/coreys/perm-usb/coreys/Documents/instacart/analyze_instacart_data/data/external/instacart_2017_05_01/order_products__prior.csv' DELIMITER ',' CSV HEADER ;

COPY public.order_products__train (order_id, product_id, add_to_cart_order, reordered)
FROM '/home/coreys/perm-usb/coreys/Documents/instacart/analyze_instacart_data/data/external/instacart_2017_05_01/order_products__train.csv' DELIMITER ',' CSV HEADER ;
