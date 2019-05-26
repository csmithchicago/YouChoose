-- query to get (product, customer) connections for bipartite graph,
-- and insert into customer_products table

select * into customer_products from
(
  SELECT p.product_id, o.user_id from order_products__prior as p       
  left join
  (select order_id, user_id from orders) o
  on o.order_id=p.order_id
 ) as c_p
