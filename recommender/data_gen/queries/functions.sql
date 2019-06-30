-- FUNCTION: public.array_contains(anyarray, integer)

-- DROP FUNCTION public.array_contains(anyarray, integer);

CREATE OR REPLACE FUNCTION public.array_contains(
	arr anyarray,
	val integer)
    RETURNS integer
    LANGUAGE 'sql'

    COST 100
    VOLATILE
AS $BODY$SELECT
case when count(*)::integer > 0 then 1
else 0
end
FROM unnest(arr)
where exists (select * from unnest(arr) as q
			  where q=val)
LIMIT 1;
$BODY$;

ALTER FUNCTION public.array_contains(anyarray, integer)
    OWNER TO postgres;


-- FUNCTION: public.multiply_arrays_nonzero(anyarray, anyarray)

-- DROP FUNCTION public.multiply_arrays_nonzero(anyarray, anyarray);

CREATE OR REPLACE FUNCTION public.multiply_arrays_nonzero(
	arr_1 anyarray,
	arr_2 anyarray)
    RETURNS anyarray
    LANGUAGE 'sql'

    COST 100
    VOLATILE
AS $BODY$SELECT ARRAY(
	SELECT a * b
     FROM unnest(
       arr_1, -- ex1
       arr_2  -- ex2
     ) AS t(a,b)
 	  where a != 0 and b != 0
);$BODY$;

ALTER FUNCTION public.multiply_arrays_nonzero(anyarray, anyarray)
    OWNER TO postgres;

-- remove single element from array
CREATE OR REPLACE FUNCTION public.slow_pop(anyarray, idx integer DEFAULT 1)
    RETURNS anyarray
    LANGUAGE 'sql'

    IMMUTABLE
    AS 'SELECT $1[:$2-1] || $1[$2+1:]';


SELECT slow_pop('{foo,bar,baz}'::text[], 3) AS t;

-- create directed node tuples from products in ass to cart order
CREATE OR REPLACE FUNCTION public.directed_nodes(prod_list anyarray)
    RETURNS Table(f int, t int) AS
    'SELECT unnest(prod_list[:(array_upper($1, 1)-1)]), unnest(prod_list[2:])'
    LANGUAGE 'sql'
    IMMUTABLE ;

ALTER FUNCTION public.directed_nodes(anyarray)
    OWNER TO postgres;

SELECT public.directed_nodes(ARRAY[2,3,4,5]) AS t, ARRAY[2,3,4,5];

