SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.categories (
    category_id integer NOT NULL,
    name character varying(80) NOT NULL,
    parent_id integer
);


--
-- Name: categories_category_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.categories ALTER COLUMN category_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.categories_category_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: customers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.customers (
    customer_id integer NOT NULL,
    first_name character varying(50) NOT NULL,
    last_name character varying(50) NOT NULL,
    email character varying(120) NOT NULL,
    phone character varying(20),
    city character varying(60),
    country character varying(60) DEFAULT 'India'::character varying NOT NULL,
    loyalty_points integer DEFAULT 0 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT customers_loyalty_points_check CHECK ((loyalty_points >= 0))
);


--
-- Name: customers_customer_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.customers ALTER COLUMN customer_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.customers_customer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.order_items (
    order_item_id integer NOT NULL,
    order_id integer NOT NULL,
    product_id integer NOT NULL,
    quantity integer NOT NULL,
    unit_price numeric(10,2) NOT NULL,
    CONSTRAINT order_items_quantity_check CHECK ((quantity > 0)),
    CONSTRAINT order_items_unit_price_check CHECK ((unit_price > (0)::numeric))
);


--
-- Name: order_items_order_item_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.order_items ALTER COLUMN order_item_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.order_items_order_item_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orders (
    order_id integer NOT NULL,
    customer_id integer NOT NULL,
    order_date timestamp without time zone DEFAULT now() NOT NULL,
    status character varying(20) DEFAULT 'pending'::character varying NOT NULL,
    payment_method character varying(30) NOT NULL,
    shipping_city character varying(60),
    shipping_country character varying(60) DEFAULT 'India'::character varying NOT NULL,
    total_amount numeric(12,2) DEFAULT 0 NOT NULL,
    CONSTRAINT orders_status_check CHECK (((status)::text = ANY ((ARRAY['pending'::character varying, 'processing'::character varying, 'shipped'::character varying, 'delivered'::character varying, 'cancelled'::character varying, 'returned'::character varying])::text[]))),
    CONSTRAINT orders_total_amount_check CHECK ((total_amount >= (0)::numeric))
);


--
-- Name: orders_order_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.orders ALTER COLUMN order_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.orders_order_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.products (
    product_id integer NOT NULL,
    sku character varying(20) NOT NULL,
    name character varying(150) NOT NULL,
    brand character varying(60),
    category_id integer NOT NULL,
    price numeric(10,2) NOT NULL,
    cost numeric(10,2) NOT NULL,
    stock_qty integer DEFAULT 0 NOT NULL,
    is_available boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_price_above_cost CHECK ((price >= cost)),
    CONSTRAINT products_cost_check CHECK ((cost >= (0)::numeric)),
    CONSTRAINT products_price_check CHECK ((price > (0)::numeric)),
    CONSTRAINT products_stock_qty_check CHECK ((stock_qty >= 0))
);


--
-- Name: products_product_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.products ALTER COLUMN product_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.products_product_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: reviews; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.reviews (
    review_id integer NOT NULL,
    product_id integer NOT NULL,
    customer_id integer NOT NULL,
    rating smallint NOT NULL,
    comment text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT reviews_rating_check CHECK (((rating >= 1) AND (rating <= 5)))
);


--
-- Name: reviews_review_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

ALTER TABLE public.reviews ALTER COLUMN review_id ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME public.reviews_review_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.categories (category_id, name, parent_id) FROM stdin;
1	Electronics	\N
2	Clothing	\N
3	Home & Kitchen	\N
4	Books	\N
5	Sports	\N
6	Smartphones	1
7	Laptops	1
8	Headphones	1
\.


--
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.customers (customer_id, first_name, last_name, email, phone, city, country, loyalty_points, is_active, created_at) FROM stdin;
1	Aarav	Sharma	aarav.sharma@example.com	9820011111	Mumbai	India	1200	t	2025-06-01 04:30:00+00
2	Priya	Patel	priya.patel@example.com	9820022222	Ahmedabad	India	800	t	2025-06-15 06:00:00+00
3	Rohan	Mehta	rohan.mehta@example.com	9820033333	Pune	India	450	t	2025-07-02 03:45:00+00
4	Ananya	Iyer	ananya.iyer@example.com	9820044444	Chennai	India	150	t	2025-08-10 08:30:00+00
5	Vikram	Singh	vikram.singh@example.com	9820055555	Delhi	India	2100	t	2025-08-22 11:15:00+00
6	Sneha	Reddy	sneha.reddy@example.com	9820066666	Hyderabad	India	600	t	2025-09-05 06:30:00+00
7	Arjun	Nair	arjun.nair@example.com	9820077777	Kochi	India	300	t	2025-09-18 03:00:00+00
8	Kavya	Menon	kavya.menon@example.com	9820088888	Bengaluru	India	1750	t	2025-10-01 13:30:00+00
9	Rahul	Verma	rahul.verma@example.com	\N	Lucknow	India	0	t	2025-10-20 07:50:00+00
10	Isha	Gupta	isha.gupta@example.com	9820099999	Mumbai	India	950	t	2025-11-03 04:40:00+00
11	John	Smith	john.smith@example.co.uk	447700900001	London	UK	500	t	2025-11-15 15:00:00+00
12	Emily	Johnson	emily.johnson@example.com	12125550123	New York	USA	700	t	2025-12-01 22:30:00+00
13	Liam	Chen	liam.chen@example.com	6591234567	Singapore	Singapore	250	t	2025-12-12 03:11:00+00
14	Sara	Khan	sara.khan@example.com	9820012345	Delhi	India	50	f	2026-01-04 03:30:00+00
15	Dev	Malhotra	dev.malhotra@example.com	9820054321	Jaipur	India	100	t	2026-01-20 12:30:00+00
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.order_items (order_item_id, order_id, product_id, quantity, unit_price) FROM stdin;
1	1	1	1	79999.00
2	1	7	2	1499.00
3	2	15	2	499.00
4	2	16	1	299.00
5	2	14	1	599.00
6	3	9	1	3499.00
7	3	10	2	1799.00
8	4	6	1	29990.00
9	5	3	1	55999.00
10	6	13	1	7999.00
11	6	12	1	2799.00
12	7	2	1	64999.00
13	8	17	1	3200.00
14	8	15	1	499.00
15	9	20	1	2499.00
16	9	18	2	799.00
17	10	4	1	62999.00
18	10	8	1	5999.00
19	11	6	1	29990.00
20	11	11	3	1299.00
21	12	5	1	42999.00
22	13	8	2	5999.00
23	13	14	3	599.00
24	14	1	1	79999.00
25	15	9	2	3499.00
26	16	13	1	7999.00
27	16	7	1	1499.00
28	17	19	2	899.00
29	17	18	1	799.00
30	18	17	2	3200.00
31	18	16	2	299.00
32	19	10	1	1799.00
33	19	11	1	1299.00
34	20	2	1	64999.00
35	20	8	1	5999.00
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orders (order_id, customer_id, order_date, status, payment_method, shipping_city, shipping_country, total_amount) FROM stdin;
1	1	2026-01-05 10:15:00	delivered	UPI	Mumbai	India	82997.00
2	2	2026-01-12 14:30:00	delivered	Credit Card	Ahmedabad	India	1896.00
3	3	2026-02-03 09:45:00	delivered	COD	Pune	India	7097.00
4	1	2026-02-14 20:10:00	delivered	Credit Card	Mumbai	India	29990.00
5	4	2026-02-20 11:00:00	cancelled	UPI	Chennai	India	55999.00
6	5	2026-03-02 16:25:00	delivered	Debit Card	Delhi	India	10798.00
7	6	2026-03-15 13:40:00	shipped	UPI	Hyderabad	India	64999.00
8	7	2026-03-28 18:05:00	delivered	Net Banking	Kochi	India	3699.00
9	8	2026-04-04 12:50:00	delivered	UPI	Bengaluru	India	4097.00
10	10	2026-04-18 15:15:00	delivered	Credit Card	Mumbai	India	68998.00
11	11	2026-05-01 10:00:00	delivered	PayPal	London	UK	33887.00
12	12	2026-05-09 21:30:00	returned	Credit Card	New York	USA	42999.00
13	2	2026-06-10 17:20:00	delivered	UPI	Ahmedabad	India	13795.00
14	13	2026-06-22 08:55:00	shipped	Credit Card	Singapore	Singapore	79999.00
15	5	2026-07-07 19:45:00	pending	UPI	Delhi	India	6998.00
16	1	2026-08-01 11:35:00	shipped	Credit Card	Mumbai	India	9498.00
17	15	2026-08-19 14:00:00	pending	COD	Jaipur	India	2597.00
18	8	2026-09-05 10:20:00	delivered	UPI	Bengaluru	India	6998.00
19	10	2026-09-25 16:10:00	processing	Debit Card	Mumbai	India	3098.00
20	3	2026-10-10 12:00:00	processing	UPI	Pune	India	70998.00
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.products (product_id, sku, name, brand, category_id, price, cost, stock_qty, is_available, created_at) FROM stdin;
1	PH-001	Samsung Galaxy S24	Samsung	6	79999.00	62000.00	25	t	2026-10-21 07:47:06.357604+00
2	PH-002	OnePlus 12	OnePlus	6	64999.00	51000.00	40	t	2026-10-21 07:47:06.357604+00
3	LT-001	Dell Inspiron 15	Dell	7	55999.00	44000.00	15	t	2026-10-21 07:47:06.357604+00
4	LT-002	HP Pavilion 14	HP	7	62999.00	50000.00	12	t	2026-10-21 07:47:06.357604+00
5	LT-003	Lenovo IdeaPad Slim 3	Lenovo	7	42999.00	34000.00	30	t	2026-10-21 07:47:06.357604+00
6	HP-001	Sony WH-1000XM5	Sony	8	29990.00	21000.00	18	t	2026-10-21 07:47:06.357604+00
7	HP-002	boAt Rockerz 450	boAt	8	1499.00	800.00	200	t	2026-10-21 07:47:06.357604+00
8	HP-003	JBL Tune 760NC	JBL	8	5999.00	3800.00	60	t	2026-10-21 07:47:06.357604+00
9	CL-001	Levi's 511 Slim Jeans	Levi's	2	3499.00	1900.00	90	t	2026-10-21 07:47:06.357604+00
10	CL-002	Allen Solly Formal Shirt	Allen Solly	2	1799.00	900.00	120	t	2026-10-21 07:47:06.357604+00
11	CL-003	Nike Running T-Shirt	Nike	2	1299.00	650.00	150	t	2026-10-21 07:47:06.357604+00
12	HK-001	Prestige Induction Cooktop	Prestige	3	2799.00	1800.00	45	t	2026-10-21 07:47:06.357604+00
13	HK-002	Philips Air Fryer	Philips	3	7999.00	5200.00	35	t	2026-10-21 07:47:06.357604+00
14	HK-003	Milton Steel Bottle	Milton	3	599.00	250.00	300	t	2026-10-21 07:47:06.357604+00
15	BK-001	Atomic Habits	Penguin	4	499.00	250.00	180	t	2026-10-21 07:47:06.357604+00
16	BK-002	The Alchemist	HarperCollins	4	299.00	140.00	220	t	2026-10-21 07:47:06.357604+00
17	BK-003	Clean Code	Pearson	4	3200.00	2000.00	40	t	2026-10-21 07:47:06.357604+00
18	SP-001	Yoga Mat	Decathlon	5	799.00	350.00	100	t	2026-10-21 07:47:06.357604+00
19	SP-002	Cosco Football	Cosco	5	899.00	450.00	0	f	2026-10-21 07:47:06.357604+00
20	SP-003	Yonex Badminton Racket	Yonex	5	2499.00	1500.00	55	t	2026-10-21 07:47:06.357604+00
21	EL-001	Logitech Wireless Mouse	Logitech	1	899.00	500.00	75	t	2026-10-21 07:47:06.357604+00
\.


--
-- Data for Name: reviews; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.reviews (review_id, product_id, customer_id, rating, comment, created_at) FROM stdin;
1	1	1	5	Excellent camera and display	2026-01-20 10:00:00+00
2	7	1	4	Good value for money	2026-01-21 10:00:00+00
3	6	1	5	Best noise cancellation I have used	2026-03-01 09:00:00+00
4	15	2	5	Life changing book	2026-01-25 18:00:00+00
5	16	2	4	Beautiful short read	2026-01-26 18:00:00+00
6	9	3	3	Fit is okay, colour faded a bit	2026-02-15 12:00:00+00
7	10	3	4	Great for office wear	2026-02-16 12:00:00+00
8	13	5	5	Cooks evenly and saves oil	2026-03-20 20:00:00+00
9	12	5	4	Works well, a bit heavy	2026-03-21 20:00:00+00
10	17	7	5	Must read for every developer	2026-04-05 09:30:00+00
11	20	8	4	Light and well balanced	2026-04-15 17:00:00+00
12	18	8	3	Slightly thin	2026-04-16 17:00:00+00
13	4	10	4	Smooth performance for the price	2026-05-10 14:00:00+00
14	6	11	5	Worth every penny	2026-05-20 08:00:00+00
15	5	12	2	Stopped working, had to return	2026-05-30 22:00:00+00
16	8	2	4	Solid sound, comfortable fit	2026-06-25 11:00:00+00
17	11	11	3	\N	2026-05-22 08:30:00+00
\.


--
-- Name: categories_category_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.categories_category_id_seq', 8, true);


--
-- Name: customers_customer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.customers_customer_id_seq', 17, true);


--
-- Name: order_items_order_item_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.order_items_order_item_id_seq', 37, true);


--
-- Name: orders_order_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orders_order_id_seq', 22, true);


--
-- Name: products_product_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.products_product_id_seq', 22, true);


--
-- Name: reviews_review_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.reviews_review_id_seq', 18, true);


--
-- Name: categories categories_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_name_key UNIQUE (name);


--
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (category_id);


--
-- Name: customers customers_email_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_email_key UNIQUE (email);


--
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customer_id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (order_item_id);


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
-- Name: products products_sku_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_sku_key UNIQUE (sku);


--
-- Name: reviews reviews_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_pkey PRIMARY KEY (review_id);


--
-- Name: reviews uq_one_review_per_customer; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT uq_one_review_per_customer UNIQUE (product_id, customer_id);


--
-- Name: order_items uq_order_product; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT uq_order_product UNIQUE (order_id, product_id);


--
-- Name: idx_customers_city; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_customers_city ON public.customers USING btree (city);


--
-- Name: idx_order_items_product; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_order_items_product ON public.order_items USING btree (product_id);


--
-- Name: idx_orders_customer; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_orders_customer ON public.orders USING btree (customer_id);


--
-- Name: idx_orders_open; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_orders_open ON public.orders USING btree (status) WHERE ((status)::text = ANY ((ARRAY['pending'::character varying, 'processing'::character varying])::text[]));


--
-- Name: idx_orders_order_date; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_orders_order_date ON public.orders USING btree (order_date);


--
-- Name: idx_products_category; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_products_category ON public.products USING btree (category_id);


--
-- Name: idx_products_name_lower; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_products_name_lower ON public.products USING btree (lower((name)::text));


--
-- Name: idx_reviews_product; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX idx_reviews_product ON public.reviews USING btree (product_id);


--
-- Name: categories categories_parent_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_parent_id_fkey FOREIGN KEY (parent_id) REFERENCES public.categories(category_id) ON DELETE SET NULL;


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(order_id) ON DELETE CASCADE;


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id);


--
-- Name: orders orders_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id);


--
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_category_id_fkey FOREIGN KEY (category_id) REFERENCES public.categories(category_id);


--
-- Name: reviews reviews_customer_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_customer_id_fkey FOREIGN KEY (customer_id) REFERENCES public.customers(customer_id) ON DELETE CASCADE;


--
-- Name: reviews reviews_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.reviews
    ADD CONSTRAINT reviews_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(product_id) ON DELETE CASCADE;


