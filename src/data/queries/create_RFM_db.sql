SELECT t1.user_id, t1.T as lifetime, t2.frequency as frequency
FROM
	(SELECT user_id, CAST (SUM (days_since_prior) as INT) as T
		FROM orders
		where eval_set='prior'
		GROUP BY user_id) t1
LEFT JOIN
	(SELECT user_id, COUNT (DISTINCT order_id) as frequency
		FROM orders
		where eval_set='prior'
		GROUP BY user_id) t2
ON
	(t1.user_id=t2.user_id)
;


SELECT t1.user_id, t1.T as lifetime, t2.days_since_prior as last_order
FROM
	(SELECT user_id, CAST (SUM (days_since_prior) as INT) as T
		FROM orders
		where eval_set='prior'
		GROUP BY user_id) t1
FULL JOIN
(SELECT user_id, CAST(days_since_prior as INT) FROM orders
	WHERE order_id in (	SELECT t.last_order_id
					   	FROM (
						SELECT user_id,
						MAX(order_id) as last_order_id
						FROM orders
						where eval_set='prior'
						GROUP BY user_id) t
						)
	) t2
ON
	(t1.user_id=t2.user_id)

ORDER BY t1.user_id ASC
;

SELECT t1.user_id, t1.T as lifetime, t2.days_since_prior as last_order
FROM
	(SELECT user_id, CAST (SUM (days_since_prior) as INT) as T
		FROM orders
		where eval_set='prior'
		GROUP BY user_id) t1
FULL JOIN
(SELECT user_id, days_since_prior FROM orders
	WHERE order_number in (SELECT t.last_order
					   	FROM (
						SELECT user_id,
						MAX(order_number) as last_order
						FROM orders
						where eval_set='prior'
						GROUP BY user_id) t
						)
) t2
ON
	(t1.user_id=t2.user_id)

ORDER BY t1.user_id ASC
;






