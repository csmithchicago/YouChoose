-- insert the product pairs into new table
DROP TABLE IF EXISTS product_adjacency_map;

SELECT * INTO product_adjacency_map from
(WITH tbl AS (SELECT 
    order_id,
    array_agg(product_id ORDER BY add_to_cart_order) AS prod_list
FROM order_products__prior
GROUP BY order_id
-- LIMIT 500
)
SELECT
    t1.* AS origin,
    t2.* AS destination,
    COUNT(t1) as weight
FROM
    (SELECT unnest(tbl.prod_list) AS origin FROM tbl) AS t1
INNER JOIN
    (SELECT unnest(tbl.prod_list) AS destination FROM tbl) AS t2
ON t1 < t2
GROUP BY 1, 2
ORDER BY 1, 2
-- LIMIT 100
)
tbl
;

-- SELECT * FROM product_adjacency_map;

-- -- checking how many nodes and edges
-- SELECT SUM(t.combinations) FROM (
-- SELECT 
--     order_id,
--     cardinality(array_agg(product_id ORDER BY add_to_cart_order)) AS prod_list,
--     cardinality(array_agg(product_id ORDER BY add_to_cart_order)) * (cardinality(array_agg(product_id ORDER BY add_to_cart_order)) - 1)/2 as combinations
-- FROM order_products__prior
-- GROUP BY order_id
-- LIMIT 10) t
-- ;
