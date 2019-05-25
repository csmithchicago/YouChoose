-- select o.user_id, p.product_id, o.order_id
-- from order_products__prior as p
-- full join
-- (
--     select order_id, user_id from orders
--     where orders.eval_set='prior'
-- ) o
-- on o.order_id=p.order_id
-- order by 1
-- limit 4;


with prior_orders 
as 
(
    select order_id, user_id from orders
    where eval_set='prior'
    limit 15
)

select o.order_id, p.product_id from prior_orders as o
full JOIN
(SELECT product_id, order_id from order_products__prior) p
on o.order_id=p.order_id
;