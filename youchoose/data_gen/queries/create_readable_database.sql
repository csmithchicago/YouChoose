--
-- PostgreSQL database dump
--

-- Dumped from database version 10.7
-- Dumped by pg_dump version 10.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: instacart-transactions; Type: DATABASE; Schema: -; Owner: -
--

CREATE DATABASE "instacart-transactions" WITH TEMPLATE = template0 ENCODING = 'UTF8' LC_COLLATE = 'en_US.UTF-8' LC_CTYPE = 'en_US.UTF-8';


\connect -reuse-previous=on "dbname='instacart-transactions'"

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: aisles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.aisles (
    aisle_id smallint NOT NULL,
    aisle character varying(128)
);


--
-- Name: departments; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.departments (
    department_id smallint NOT NULL,
    department character varying(32) NOT NULL
);


--
-- Name: order_products__prior; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_products__prior (
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    add_to_cart_order integer NOT NULL,
    reordered integer NOT NULL
);


--
-- Name: order_products__test; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_products__test (
)
INHERITS (public.order_products__prior);


--
-- Name: order_products__train; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_products__train (
)
INHERITS (public.order_products__prior);


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    user_id integer NOT NULL,
    eval_set character(5) NOT NULL,
    order_number smallint NOT NULL,
    order_dow smallint NOT NULL,
    order_hour_of_day smallint NOT NULL,
    days_since_prior numeric(4,2)
);


--
-- Name: orders_no_tests; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders_no_tests (
    order_id integer,
    user_id integer,
    eval_set character(5),
    order_number smallint,
    order_dow smallint,
    order_hour_of_day smallint,
    days_since_prior numeric(4,2)
);


--
-- Name: orders_test; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders_test (
    order_id integer,
    user_id integer,
    eval_set character(5),
    order_number smallint,
    order_dow smallint,
    order_hour_of_day smallint,
    days_since_prior numeric(4,2)
);


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    product_name character varying(256) NOT NULL,
    aisle_id integer NOT NULL,
    department_id integer NOT NULL
);


--
-- Name: aisles aisles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.aisles
    ADD CONSTRAINT aisles_pkey PRIMARY KEY (aisle_id);


--
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (department_id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (order_id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (product_id);


--
-- Name: products aisle_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT aisle_id FOREIGN KEY (aisle_id) REFERENCES public.aisles(aisle_id) ON UPDATE CASCADE;


--
-- Name: products department_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT department_id FOREIGN KEY (department_id) REFERENCES public.departments(department_id) ON UPDATE CASCADE;


--
-- Name: order_products__prior order_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_products__prior
    ADD CONSTRAINT order_id FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON UPDATE CASCADE;


--
-- Name: order_products__train order_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_products__train
    ADD CONSTRAINT order_id FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON UPDATE CASCADE;


--
-- Name: order_products__test order_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_products__test
    ADD CONSTRAINT order_id FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON UPDATE CASCADE;


--
-- Name: order_products__prior product_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_products__prior
    ADD CONSTRAINT product_id FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON UPDATE CASCADE;


--
-- Name: order_products__train product_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_products__train
    ADD CONSTRAINT product_id FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON UPDATE CASCADE;


--
-- Name: order_products__test product_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_products__test
    ADD CONSTRAINT product_id FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON UPDATE CASCADE;


--
-- PostgreSQL database dump complete
--

