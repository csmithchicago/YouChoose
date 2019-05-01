COPY (
	SELECT 
		r.user_id,
		l.order_number_list[array_upper(l.order_number_list, 1)] as frequency,
		(SELECT SUM(s) FROM UNNEST(l.days_between_orders_list) s) as recency,
		(SELECT SUM(s) FROM UNNEST(l.days_between_orders_list) s) + r.days_since_prior as T
	FROM
		(SELECT user_id,  
			array_agg(order_id order by order_number) as user_orders, 
			array_agg(order_number order by order_number) as order_number_list,
			array_agg(days_since_prior order by order_number) as days_between_orders_list
		FROM orders
		Where eval_set='prior'
		GROUP BY user_id
		) l
	RIGHT JOIN
		(
			SELECT user_id, days_since_prior FROM orders WHERE eval_set='train'
		) r
	ON
	l.user_id=r.user_id

)
TO '/home/coreys/perm-usb/coreys/Documents/instacart/analyze_instacart_data/data/processed/CLV_data.csv' CSV HEADER DELIMITER ','
							
;


