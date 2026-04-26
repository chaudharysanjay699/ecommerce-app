--
-- PostgreSQL database dump
--

\restrict gKxxUpr1nv91UTJn6Q9epVoww3TIicKDsXg1DPjQjoBfJ1OfzUEWY3vBsKiU9GL

-- Dumped from database version 18.3
-- Dumped by pg_dump version 18.3

-- Started on 2026-04-26 15:24:20

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

ALTER TABLE IF EXISTS ONLY "public"."wishlist_items" DROP CONSTRAINT IF EXISTS "wishlist_items_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."wishlist_items" DROP CONSTRAINT IF EXISTS "wishlist_items_product_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."uploaded_files" DROP CONSTRAINT IF EXISTS "uploaded_files_uploaded_by_fkey";
ALTER TABLE IF EXISTS ONLY "public"."products" DROP CONSTRAINT IF EXISTS "products_category_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."otps" DROP CONSTRAINT IF EXISTS "otps_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."orders" DROP CONSTRAINT IF EXISTS "orders_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."order_tracking" DROP CONSTRAINT IF EXISTS "order_tracking_order_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."order_items" DROP CONSTRAINT IF EXISTS "order_items_product_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."order_items" DROP CONSTRAINT IF EXISTS "order_items_order_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."offers" DROP CONSTRAINT IF EXISTS "offers_product_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."notifications" DROP CONSTRAINT IF EXISTS "notifications_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."notifications" DROP CONSTRAINT IF EXISTS "fk_notifications_order_id";
ALTER TABLE IF EXISTS ONLY "public"."categories" DROP CONSTRAINT IF EXISTS "fk_categories_parent_id";
ALTER TABLE IF EXISTS ONLY "public"."device_tokens" DROP CONSTRAINT IF EXISTS "device_tokens_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."carts" DROP CONSTRAINT IF EXISTS "carts_user_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."cart_items" DROP CONSTRAINT IF EXISTS "cart_items_product_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."cart_items" DROP CONSTRAINT IF EXISTS "cart_items_cart_id_fkey";
ALTER TABLE IF EXISTS ONLY "public"."addresses" DROP CONSTRAINT IF EXISTS "addresses_user_id_fkey";
DROP INDEX IF EXISTS "public"."uq_users_phone_active";
DROP INDEX IF EXISTS "public"."uq_users_email_active";
DROP INDEX IF EXISTS "public"."ix_wishlist_items_user_id";
DROP INDEX IF EXISTS "public"."ix_wishlist_items_product_id";
DROP INDEX IF EXISTS "public"."ix_wishlist_items_id";
DROP INDEX IF EXISTS "public"."ix_users_id";
DROP INDEX IF EXISTS "public"."ix_uploaded_files_uploaded_by";
DROP INDEX IF EXISTS "public"."ix_uploaded_files_id";
DROP INDEX IF EXISTS "public"."ix_products_id";
DROP INDEX IF EXISTS "public"."ix_products_category_id";
DROP INDEX IF EXISTS "public"."ix_otps_user_id";
DROP INDEX IF EXISTS "public"."ix_otps_id";
DROP INDEX IF EXISTS "public"."ix_orders_user_id";
DROP INDEX IF EXISTS "public"."ix_orders_invoice_number";
DROP INDEX IF EXISTS "public"."ix_orders_id";
DROP INDEX IF EXISTS "public"."ix_order_tracking_order_id";
DROP INDEX IF EXISTS "public"."ix_order_tracking_id";
DROP INDEX IF EXISTS "public"."ix_order_items_product_id";
DROP INDEX IF EXISTS "public"."ix_order_items_order_id";
DROP INDEX IF EXISTS "public"."ix_order_items_id";
DROP INDEX IF EXISTS "public"."ix_offers_product_id";
DROP INDEX IF EXISTS "public"."ix_offers_id";
DROP INDEX IF EXISTS "public"."ix_notifications_user_id";
DROP INDEX IF EXISTS "public"."ix_notifications_order_id";
DROP INDEX IF EXISTS "public"."ix_notifications_id";
DROP INDEX IF EXISTS "public"."ix_device_tokens_user_id";
DROP INDEX IF EXISTS "public"."ix_device_tokens_id";
DROP INDEX IF EXISTS "public"."ix_categories_slug";
DROP INDEX IF EXISTS "public"."ix_categories_parent_id";
DROP INDEX IF EXISTS "public"."ix_categories_id";
DROP INDEX IF EXISTS "public"."ix_carts_user_id";
DROP INDEX IF EXISTS "public"."ix_carts_id";
DROP INDEX IF EXISTS "public"."ix_cart_items_product_id";
DROP INDEX IF EXISTS "public"."ix_cart_items_id";
DROP INDEX IF EXISTS "public"."ix_cart_items_cart_id";
DROP INDEX IF EXISTS "public"."ix_banners_id";
DROP INDEX IF EXISTS "public"."ix_addresses_user_id";
DROP INDEX IF EXISTS "public"."ix_addresses_id";
ALTER TABLE IF EXISTS ONLY "public"."wishlist_items" DROP CONSTRAINT IF EXISTS "wishlist_items_pkey";
ALTER TABLE IF EXISTS ONLY "public"."users" DROP CONSTRAINT IF EXISTS "users_pkey";
ALTER TABLE IF EXISTS ONLY "public"."wishlist_items" DROP CONSTRAINT IF EXISTS "uq_wishlist_user_product";
ALTER TABLE IF EXISTS ONLY "public"."cart_items" DROP CONSTRAINT IF EXISTS "uq_cart_product";
ALTER TABLE IF EXISTS ONLY "public"."uploaded_files" DROP CONSTRAINT IF EXISTS "uploaded_files_pkey";
ALTER TABLE IF EXISTS ONLY "public"."products" DROP CONSTRAINT IF EXISTS "products_pkey";
ALTER TABLE IF EXISTS ONLY "public"."otps" DROP CONSTRAINT IF EXISTS "otps_pkey";
ALTER TABLE IF EXISTS ONLY "public"."orders" DROP CONSTRAINT IF EXISTS "orders_pkey";
ALTER TABLE IF EXISTS ONLY "public"."order_tracking" DROP CONSTRAINT IF EXISTS "order_tracking_pkey";
ALTER TABLE IF EXISTS ONLY "public"."order_items" DROP CONSTRAINT IF EXISTS "order_items_pkey";
ALTER TABLE IF EXISTS ONLY "public"."offers" DROP CONSTRAINT IF EXISTS "offers_pkey";
ALTER TABLE IF EXISTS ONLY "public"."notifications" DROP CONSTRAINT IF EXISTS "notifications_pkey";
ALTER TABLE IF EXISTS ONLY "public"."device_tokens" DROP CONSTRAINT IF EXISTS "device_tokens_pkey";
ALTER TABLE IF EXISTS ONLY "public"."device_tokens" DROP CONSTRAINT IF EXISTS "device_tokens_device_token_key";
ALTER TABLE IF EXISTS ONLY "public"."categories" DROP CONSTRAINT IF EXISTS "categories_pkey";
ALTER TABLE IF EXISTS ONLY "public"."carts" DROP CONSTRAINT IF EXISTS "carts_pkey";
ALTER TABLE IF EXISTS ONLY "public"."cart_items" DROP CONSTRAINT IF EXISTS "cart_items_pkey";
ALTER TABLE IF EXISTS ONLY "public"."banners" DROP CONSTRAINT IF EXISTS "banners_pkey";
ALTER TABLE IF EXISTS ONLY "public"."app_settings" DROP CONSTRAINT IF EXISTS "app_settings_pkey";
ALTER TABLE IF EXISTS ONLY "public"."alembic_version" DROP CONSTRAINT IF EXISTS "alembic_version_pkc";
ALTER TABLE IF EXISTS ONLY "public"."addresses" DROP CONSTRAINT IF EXISTS "addresses_pkey";
DROP TABLE IF EXISTS "public"."wishlist_items";
DROP TABLE IF EXISTS "public"."users";
DROP TABLE IF EXISTS "public"."uploaded_files";
DROP TABLE IF EXISTS "public"."products";
DROP TABLE IF EXISTS "public"."otps";
DROP TABLE IF EXISTS "public"."orders";
DROP TABLE IF EXISTS "public"."order_tracking";
DROP TABLE IF EXISTS "public"."order_items";
DROP TABLE IF EXISTS "public"."offers";
DROP TABLE IF EXISTS "public"."notifications";
DROP TABLE IF EXISTS "public"."device_tokens";
DROP TABLE IF EXISTS "public"."categories";
DROP TABLE IF EXISTS "public"."carts";
DROP TABLE IF EXISTS "public"."cart_items";
DROP TABLE IF EXISTS "public"."banners";
DROP TABLE IF EXISTS "public"."app_settings";
DROP TABLE IF EXISTS "public"."alembic_version";
DROP TABLE IF EXISTS "public"."addresses";
DROP TYPE IF EXISTS "public"."orderstatus";
DROP TYPE IF EXISTS "public"."categorytype";
--
-- TOC entry 4579 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA "public"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA "public" IS 'standard public schema';


--
-- TOC entry 869 (class 1247 OID 17866)
-- Name: categorytype; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE "public"."categorytype" AS ENUM (
    'grocery',
    'vegetable',
    'basket',
    'copy_pen'
);


--
-- TOC entry 872 (class 1247 OID 17876)
-- Name: orderstatus; Type: TYPE; Schema: public; Owner: -
--

CREATE TYPE "public"."orderstatus" AS ENUM (
    'placed',
    'confirmed',
    'processing',
    'packed',
    'out_for_delivery',
    'delivered',
    'cancelled'
);


SET default_tablespace = '';

SET default_table_access_method = "heap";

--
-- TOC entry 219 (class 1259 OID 17891)
-- Name: addresses; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."addresses" (
    "user_id" "uuid" NOT NULL,
    "label" character varying(50) NOT NULL,
    "street" character varying(300) NOT NULL,
    "city" character varying(100) NOT NULL,
    "state" character varying(100) NOT NULL,
    "pincode" character varying(20) NOT NULL,
    "country" character varying(100) NOT NULL,
    "latitude" numeric(10,7),
    "longitude" numeric(10,7),
    "is_default" boolean DEFAULT false NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 220 (class 1259 OID 17910)
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL
);


--
-- TOC entry 221 (class 1259 OID 17914)
-- Name: app_settings; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."app_settings" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "store_name" character varying(200) DEFAULT 'Vidharthi Store'::character varying NOT NULL,
    "store_phone" character varying(20),
    "store_email" character varying(200),
    "store_address" "text",
    "daily_order_limit" integer,
    "order_limit_enabled" boolean DEFAULT false NOT NULL,
    "order_limit_message" character varying(500) DEFAULT 'We are currently unable to accept new orders. Please try again later.'::character varying NOT NULL,
    "delivery_charge_single" numeric(10,2) DEFAULT 10.00 NOT NULL,
    "delivery_charge_multiple" numeric(10,2) DEFAULT 15.00 NOT NULL,
    "veg_order_start_hour" integer DEFAULT 5 NOT NULL,
    "veg_order_end_hour" integer DEFAULT 9 NOT NULL,
    "veg_order_enabled" boolean DEFAULT true NOT NULL,
    "maintenance_mode" boolean DEFAULT false NOT NULL,
    "maintenance_message" character varying(500) DEFAULT 'We are currently under maintenance. Please try again later.'::character varying NOT NULL,
    "created_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "updated_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    "delivery_charge_tiers" json,
    "store_gstin" character varying(20),
    "store_pan" character varying(20),
    "store_state" character varying(100),
    "store_state_code" character varying(5),
    "default_tax_rate" numeric(5,2) DEFAULT '0'::numeric NOT NULL,
    "invoice_prefix" character varying(20) DEFAULT 'INV'::character varying NOT NULL,
    "invoice_terms" "text",
    "low_stock_threshold" integer DEFAULT 5 NOT NULL,
    "low_stock_alert_enabled" boolean DEFAULT true NOT NULL
);


--
-- TOC entry 222 (class 1259 OID 17953)
-- Name: banners; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."banners" (
    "title" character varying(200) NOT NULL,
    "image_url" character varying(500) NOT NULL,
    "link_url" character varying(500),
    "is_active" boolean DEFAULT true NOT NULL,
    "sort_order" integer DEFAULT 0 NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 223 (class 1259 OID 17969)
-- Name: cart_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."cart_items" (
    "cart_id" "uuid" NOT NULL,
    "product_id" "uuid" NOT NULL,
    "quantity" integer NOT NULL,
    "unit_price" numeric(10,2) NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 224 (class 1259 OID 17981)
-- Name: carts; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."carts" (
    "user_id" "uuid" NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 225 (class 1259 OID 17990)
-- Name: categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."categories" (
    "name" character varying(100) NOT NULL,
    "slug" character varying(120) NOT NULL,
    "type" "public"."categorytype",
    "description" "text",
    "image_url" character varying(500),
    "is_active" boolean DEFAULT true NOT NULL,
    "sort_order" integer DEFAULT 0 NOT NULL,
    "show_in_nav" boolean DEFAULT false NOT NULL,
    "show_on_top" boolean DEFAULT false NOT NULL,
    "parent_id" "uuid",
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "name_hi" character varying(100),
    "description_hi" "text"
);


--
-- TOC entry 226 (class 1259 OID 18012)
-- Name: device_tokens; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."device_tokens" (
    "user_id" "uuid" NOT NULL,
    "device_token" character varying(512) NOT NULL,
    "device_type" character varying(20) NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 227 (class 1259 OID 18025)
-- Name: notifications; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."notifications" (
    "user_id" "uuid" NOT NULL,
    "title" character varying(200) NOT NULL,
    "body" "text" NOT NULL,
    "is_read" boolean DEFAULT false NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "order_id" "uuid"
);


--
-- TOC entry 228 (class 1259 OID 18040)
-- Name: offers; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."offers" (
    "product_id" "uuid" NOT NULL,
    "title" character varying(200) NOT NULL,
    "discount_percent" numeric(5,2) NOT NULL,
    "max_uses" integer,
    "used_count" integer DEFAULT 0 NOT NULL,
    "expires_at" timestamp with time zone NOT NULL,
    "is_active" boolean DEFAULT true NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 229 (class 1259 OID 18056)
-- Name: order_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."order_items" (
    "order_id" "uuid" NOT NULL,
    "product_id" "uuid" NOT NULL,
    "quantity" integer NOT NULL,
    "unit_price" numeric(10,2) NOT NULL,
    "subtotal" numeric(10,2) NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "discount" numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    "tax_rate" numeric(5,2) DEFAULT '0'::numeric NOT NULL,
    "tax_amount" numeric(10,2) DEFAULT '0'::numeric NOT NULL,
    "hsn_code" character varying(20)
);


--
-- TOC entry 230 (class 1259 OID 18075)
-- Name: order_tracking; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."order_tracking" (
    "order_id" "uuid" NOT NULL,
    "status" "public"."orderstatus" NOT NULL,
    "description" "text",
    "changed_by" character varying(100),
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 231 (class 1259 OID 18087)
-- Name: orders; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."orders" (
    "user_id" "uuid" NOT NULL,
    "status" "public"."orderstatus" DEFAULT 'placed'::"public"."orderstatus" NOT NULL,
    "subtotal" numeric(10,2) NOT NULL,
    "delivery_charge" numeric(10,2) NOT NULL,
    "total" numeric(10,2) NOT NULL,
    "delivery_address" "text" NOT NULL,
    "notes" "text",
    "cancel_reason" character varying(300),
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "invoice_url" character varying(500),
    "shipping_label_url" character varying(500),
    "invoice_number" character varying(50)
);


--
-- TOC entry 232 (class 1259 OID 18104)
-- Name: otps; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."otps" (
    "user_id" "uuid" NOT NULL,
    "code" character varying(6) NOT NULL,
    "is_used" boolean DEFAULT false NOT NULL,
    "expires_at" character varying NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 233 (class 1259 OID 18119)
-- Name: products; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."products" (
    "name" character varying(200) NOT NULL,
    "description" "text",
    "price" numeric(10,2) NOT NULL,
    "mrp" numeric(10,2),
    "stock" integer DEFAULT 0 NOT NULL,
    "unit" character varying(50) NOT NULL,
    "image_url" character varying(500),
    "is_active" boolean DEFAULT true NOT NULL,
    "is_out_of_stock" boolean DEFAULT false NOT NULL,
    "category_id" "uuid" NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "name_hi" character varying(200),
    "description_hi" "text",
    "hsn_code" character varying(20),
    "gst_rate" numeric(5,2)
);


--
-- TOC entry 234 (class 1259 OID 18141)
-- Name: uploaded_files; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."uploaded_files" (
    "original_filename" character varying(255) NOT NULL,
    "file_path" character varying(500) NOT NULL,
    "file_url" character varying(500) NOT NULL,
    "file_size" integer NOT NULL,
    "mime_type" character varying(100) NOT NULL,
    "entity_type" character varying(50) NOT NULL,
    "entity_id" "uuid",
    "uploaded_by" "uuid",
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 235 (class 1259 OID 18157)
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."users" (
    "full_name" character varying(120) NOT NULL,
    "email" character varying(254),
    "phone" character varying(20) NOT NULL,
    "hashed_password" "text",
    "avatar_url" character varying(500),
    "is_active" boolean DEFAULT true NOT NULL,
    "is_verified" boolean DEFAULT false NOT NULL,
    "is_admin" boolean DEFAULT false NOT NULL,
    "id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "is_super_admin" boolean DEFAULT false NOT NULL,
    "is_deleted" boolean DEFAULT false NOT NULL,
    "deleted_at" timestamp with time zone
);


--
-- TOC entry 236 (class 1259 OID 18179)
-- Name: wishlist_items; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE "public"."wishlist_items" (
    "id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "product_id" "uuid" NOT NULL,
    "created_at" timestamp with time zone DEFAULT "now"() NOT NULL,
    "updated_at" timestamp with time zone DEFAULT "now"() NOT NULL
);


--
-- TOC entry 4556 (class 0 OID 17891)
-- Dependencies: 219
-- Data for Name: addresses; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."addresses" ("user_id", "label", "street", "city", "state", "pincode", "country", "latitude", "longitude", "is_default", "id", "created_at", "updated_at") FROM stdin;
9bf932ac-f606-41ed-9aa5-333eed1a84c3	home	B-180, new ashok nagar	New delhi	Delhi	110096	India	\N	\N	f	5d8b1151-594b-435a-b845-f9c7da9c6824	2026-04-25 11:12:43.104042+00	2026-04-25 11:12:43.104042+00
\.


--
-- TOC entry 4557 (class 0 OID 17910)
-- Dependencies: 220
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."alembic_version" ("version_num") FROM stdin;
0012_drop_old_idx
\.


--
-- TOC entry 4558 (class 0 OID 17914)
-- Dependencies: 221
-- Data for Name: app_settings; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."app_settings" ("id", "store_name", "store_phone", "store_email", "store_address", "daily_order_limit", "order_limit_enabled", "order_limit_message", "delivery_charge_single", "delivery_charge_multiple", "veg_order_start_hour", "veg_order_end_hour", "veg_order_enabled", "maintenance_mode", "maintenance_message", "created_at", "updated_at", "delivery_charge_tiers", "store_gstin", "store_pan", "store_state", "store_state_code", "default_tax_rate", "invoice_prefix", "invoice_terms", "low_stock_threshold", "low_stock_alert_enabled") FROM stdin;
ecce3375-a82a-4274-b016-1e28e95c1166	Vidharthi Store	\N	\N	\N	3	t	We are currently unable to accept new orders. Please try again later.	10.00	15.00	5	9	t	f	We are currently under maintenance. Please try again later.	2026-04-21 15:13:16.390805+00	2026-04-26 06:13:09.507264+00	[{"min_price": 1.0, "max_price": 299.0, "delivery_charge": 30.0}, {"min_price": 300.0, "max_price": 499.0, "delivery_charge": 15.0}]	\N	\N	\N	\N	0.00	INV	\N	5	t
\.


--
-- TOC entry 4559 (class 0 OID 17953)
-- Dependencies: 222
-- Data for Name: banners; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."banners" ("title", "image_url", "link_url", "is_active", "sort_order", "id", "created_at", "updated_at") FROM stdin;
\.


--
-- TOC entry 4560 (class 0 OID 17969)
-- Dependencies: 223
-- Data for Name: cart_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."cart_items" ("cart_id", "product_id", "quantity", "unit_price", "id", "created_at", "updated_at") FROM stdin;
37e97e11-da29-4972-9e89-c90675bcfb39	359841ea-902c-40b4-8a86-006fcb45f091	1	479.00	6d1e66a6-84c9-4cb2-a0f0-f72499f54a12	2026-04-25 09:32:37.991889+00	2026-04-25 09:32:37.991889+00
ea491c22-8fd5-4af3-83f9-8a44b93a1604	c885788e-3df5-4ea3-b21d-a37c1b4d5050	1	31.00	d713a2c1-fe62-4171-a367-dd786e3c1fad	2026-04-26 06:12:33.056561+00	2026-04-26 06:12:33.056561+00
ea491c22-8fd5-4af3-83f9-8a44b93a1604	359841ea-902c-40b4-8a86-006fcb45f091	1	479.00	23c5d44a-ee72-4bc8-be64-932f0e2fbd28	2026-04-26 06:14:05.029676+00	2026-04-26 06:14:05.029676+00
37e97e11-da29-4972-9e89-c90675bcfb39	27307022-6b56-49b5-a01a-23011dd7448f	1	28.00	fd8463e8-818c-43c3-94a9-3d0fb6f07a0c	2026-04-26 07:45:04.800269+00	2026-04-26 07:45:04.800269+00
f1c71ea0-874c-47ac-9099-fffe66852595	9467ea61-4561-4d03-beba-cc2581da9287	1	30.00	7905e200-977d-46cd-b540-f6c8ace1854c	2026-04-26 09:24:04.451326+00	2026-04-26 09:24:04.451326+00
\.


--
-- TOC entry 4561 (class 0 OID 17981)
-- Dependencies: 224
-- Data for Name: carts; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."carts" ("user_id", "id", "created_at", "updated_at") FROM stdin;
81c6f7c3-b029-40de-ac9f-1a9de870ffb7	37e97e11-da29-4972-9e89-c90675bcfb39	2026-04-25 08:52:57.818544+00	2026-04-25 08:52:57.818544+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	f1c71ea0-874c-47ac-9099-fffe66852595	2026-04-25 11:12:02.801511+00	2026-04-25 11:12:02.801511+00
4bba9ed9-7f55-4d34-b828-d81565054406	ea491c22-8fd5-4af3-83f9-8a44b93a1604	2026-04-26 06:12:33.056561+00	2026-04-26 06:12:33.056561+00
\.


--
-- TOC entry 4562 (class 0 OID 17990)
-- Dependencies: 225
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."categories" ("name", "slug", "type", "description", "image_url", "is_active", "sort_order", "show_in_nav", "show_on_top", "parent_id", "id", "created_at", "updated_at", "is_deleted", "name_hi", "description_hi") FROM stdin;
Atta, Flours & Sooji	atta-flours-sooji	\N	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/d39283234da64f4ca17f4ac9df06644a.webp	t	0	f	f	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	0f3cf1c1-769d-4561-a34f-4b66276fc798	2026-04-25 08:46:40.616042+00	2026-04-25 08:50:55.132915+00	f		
Dals & Pulses	dals-pulses	\N	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/76d4e67ac33a4cdfa91fad2010218681.webp	t	0	f	f	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	2a40baea-d8f9-45ad-88a6-d410c3897367	2026-04-25 08:56:43.09151+00	2026-04-25 08:56:43.09151+00	f	\N	\N
Rice	rice	\N	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/51047edfa1844f719f1664daf5c624f5.webp	t	0	f	f	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	b38c0995-f7c0-45e6-8bbc-0f356d77848b	2026-04-25 08:57:13.714966+00	2026-04-25 08:57:13.714966+00	f	\N	\N
Salt, Sugar & Jaggery	salt-sugar-jaggery	\N	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/492301166dba4b4caef63e7830227b60.webp	t	0	f	f	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	d1d250d3-3356-4750-8f66-62c82c7cd854	2026-04-25 08:58:13.084032+00	2026-04-25 08:58:13.084032+00	f	\N	\N
Edible Oils	edible-oils	\N	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/a2c48066d8f9401db9cca9ddc7eebb95.webp	t	0	f	f	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	0a9ac04f-587c-452f-9ee0-9b01a2723947	2026-04-25 09:00:19.730821+00	2026-04-25 09:00:19.730821+00	f	\N	\N
Masala, Spices & Mukhwas	masala-spices-mukhwas	\N	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/b13c63379b1547649c9e6756c938bbc0.webp	t	0	f	f	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	72574126-2071-4bcb-9cbe-6caef475a4e3	2026-04-25 09:01:08.339561+00	2026-04-25 09:01:08.339561+00	f	\N	\N
Wheat & Soya	wheat-soya	\N	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/10cd5b49f9b34522a76bb0d3840afa4c.webp	t	0	f	f	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	a0db8abd-0308-4c08-ae35-927cd5e258aa	2026-04-25 09:01:54.361944+00	2026-04-25 09:01:54.361944+00	f	\N	\N
Dry Fruits & Nuts	dry-fruits-nuts	\N	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/4d9ccabd133f414f8c26740602541d81.png	t	0	f	f	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	d501a309-2d51-492c-96d7-7f78a838966b	2026-04-26 07:37:30.401257+00	2026-04-26 07:53:50.900202+00	f		
Vegitables	vegitables	vegetable	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/792dfaf5501240578eb09a3dbf900cfb.png	t	0	t	f	\N	893a2be3-24a0-4eb7-a121-3e686a48a217	2026-04-25 08:54:58.489442+00	2026-04-25 12:11:14.332004+00	f	सब्ज़ियाँ	
Grocery	grocery	grocery	\N	https://ecommerce.vidharthigeneralstore.in/uploads/categories/9ba0fd37d5f94128b33ecce1fc344304.png	t	0	t	f	\N	5233693f-6ba1-4b8a-8df4-6c2ec1c28156	2026-04-25 08:46:16.942912+00	2026-04-25 18:31:07.936413+00	f	किराना	
\.


--
-- TOC entry 4563 (class 0 OID 18012)
-- Dependencies: 226
-- Data for Name: device_tokens; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."device_tokens" ("user_id", "device_token", "device_type", "id", "created_at", "updated_at") FROM stdin;
\.


--
-- TOC entry 4564 (class 0 OID 18025)
-- Dependencies: 227
-- Data for Name: notifications; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."notifications" ("user_id", "title", "body", "is_read", "id", "created_at", "updated_at", "order_id") FROM stdin;
81c6f7c3-b029-40de-ac9f-1a9de870ffb7	Order Placed	Your order #033ce432-08b6-40f1-8e5a-12b819d1fc4a has been placed. Total: ₹489.0	t	8bed8d7b-2526-4b0e-b7ec-f682e9f707fc	2026-04-25 08:53:10.138396+00	2026-04-25 09:34:08.912959+00	033ce432-08b6-40f1-8e5a-12b819d1fc4a
81c6f7c3-b029-40de-ac9f-1a9de870ffb7	Order Update	Your order #033ce432-08b6-40f1-8e5a-12b819d1fc4a status is now: confirmed.	t	7f58919a-0921-492b-985b-6bb3eec54511	2026-04-25 08:53:26.461667+00	2026-04-25 09:34:08.912959+00	033ce432-08b6-40f1-8e5a-12b819d1fc4a
9bf932ac-f606-41ed-9aa5-333eed1a84c3	Order Placed	Your order #0bef612b-0edf-4c3a-9fba-00c6ca40b6d6 has been placed. Total: ₹61.0	t	b3d6371e-2d99-400b-bf51-5ca3175f1ce5	2026-04-25 11:17:11.573312+00	2026-04-26 09:11:56.435968+00	0bef612b-0edf-4c3a-9fba-00c6ca40b6d6
9bf932ac-f606-41ed-9aa5-333eed1a84c3	Order Placed	Your order #154be291-f31d-45f1-b03f-2170de980f93 has been placed. Total: ₹69.0	t	c04fa23c-d62c-4ea7-9593-3dd700fc61d6	2026-04-26 05:22:24.069353+00	2026-04-26 09:11:56.435968+00	154be291-f31d-45f1-b03f-2170de980f93
9bf932ac-f606-41ed-9aa5-333eed1a84c3	Order Placed	Your order #6bbde858-c1d1-4cba-9699-2f92763e9ddb has been placed. Total: ₹60.0	f	31eb5800-63f8-4571-803b-0f56b2106120	2026-04-26 09:12:16.267164+00	2026-04-26 09:12:16.267164+00	6bbde858-c1d1-4cba-9699-2f92763e9ddb
\.


--
-- TOC entry 4565 (class 0 OID 18040)
-- Dependencies: 228
-- Data for Name: offers; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."offers" ("product_id", "title", "discount_percent", "max_uses", "used_count", "expires_at", "is_active", "id", "created_at", "updated_at") FROM stdin;
\.


--
-- TOC entry 4566 (class 0 OID 18056)
-- Dependencies: 229
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."order_items" ("order_id", "product_id", "quantity", "unit_price", "subtotal", "id", "created_at", "updated_at", "discount", "tax_rate", "tax_amount", "hsn_code") FROM stdin;
033ce432-08b6-40f1-8e5a-12b819d1fc4a	359841ea-902c-40b4-8a86-006fcb45f091	1	479.00	479.00	bee37726-b5f3-4c63-b5d2-95d72737c91e	2026-04-25 08:53:10.138396+00	2026-04-25 08:53:10.138396+00	0.00	0.00	0.00	\N
0bef612b-0edf-4c3a-9fba-00c6ca40b6d6	c885788e-3df5-4ea3-b21d-a37c1b4d5050	1	31.00	31.00	a2643500-3ab4-487a-9df5-eb05fc53541d	2026-04-25 11:17:11.573312+00	2026-04-25 11:17:11.573312+00	0.00	0.00	0.00	\N
154be291-f31d-45f1-b03f-2170de980f93	b7ea41dc-bbb8-46a0-aa20-7df8f62245fd	1	39.00	39.00	5e73be05-1320-49d2-bbff-efd0b356a34a	2026-04-26 05:22:24.069353+00	2026-04-26 05:22:24.069353+00	0.00	0.00	0.00	\N
6bbde858-c1d1-4cba-9699-2f92763e9ddb	9467ea61-4561-4d03-beba-cc2581da9287	1	30.00	30.00	f3713c88-42d8-4d30-a654-736394a767fe	2026-04-26 09:12:16.267164+00	2026-04-26 09:12:16.267164+00	0.00	0.00	0.00	\N
\.


--
-- TOC entry 4567 (class 0 OID 18075)
-- Dependencies: 230
-- Data for Name: order_tracking; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."order_tracking" ("order_id", "status", "description", "changed_by", "id", "created_at", "updated_at") FROM stdin;
033ce432-08b6-40f1-8e5a-12b819d1fc4a	placed	Order placed successfully	system	6fe03271-3d17-4399-a3dc-2a551506c017	2026-04-25 08:53:10.138396+00	2026-04-25 08:53:10.138396+00
033ce432-08b6-40f1-8e5a-12b819d1fc4a	confirmed	\N	admin	e0007f64-f5b3-4f18-bda5-87b466ebe011	2026-04-25 08:53:26.461667+00	2026-04-25 08:53:26.461667+00
0bef612b-0edf-4c3a-9fba-00c6ca40b6d6	placed	Order placed successfully	system	bd25c49f-cec0-4790-a0ca-b5f08dd4e03f	2026-04-25 11:17:11.573312+00	2026-04-25 11:17:11.573312+00
154be291-f31d-45f1-b03f-2170de980f93	placed	Order placed successfully	system	14aded8f-c3ec-4dbe-8929-f6acb7e91fe3	2026-04-26 05:22:24.069353+00	2026-04-26 05:22:24.069353+00
6bbde858-c1d1-4cba-9699-2f92763e9ddb	placed	Order placed successfully	system	d75e51c6-b687-4abb-8865-f8eb4cd3278a	2026-04-26 09:12:16.267164+00	2026-04-26 09:12:16.267164+00
\.


--
-- TOC entry 4568 (class 0 OID 18087)
-- Dependencies: 231
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."orders" ("user_id", "status", "subtotal", "delivery_charge", "total", "delivery_address", "notes", "cancel_reason", "id", "created_at", "updated_at", "invoice_url", "shipping_label_url", "invoice_number") FROM stdin;
81c6f7c3-b029-40de-ac9f-1a9de870ffb7	confirmed	479.00	10.00	489.00	B 1204 Tower 1, Oak Yahavi, OCR 9\n\nVanaha Township Lavale PIRANGUT		\N	033ce432-08b6-40f1-8e5a-12b819d1fc4a	2026-04-25 08:53:10.138396+00	2026-04-25 08:53:26.461667+00	https://ecommerce.vidharthigeneralstore.in/uploads/pdfs/invoice_033ce432-08b6-40f1-8e5a-12b819d1fc4a.pdf	https://ecommerce.vidharthigeneralstore.in/uploads/pdfs/shipping_label_033ce432-08b6-40f1-8e5a-12b819d1fc4a.pdf	INV-2026-0001
9bf932ac-f606-41ed-9aa5-333eed1a84c3	placed	31.00	30.00	61.00	B-180, new ashok nagar, New delhi, Delhi - 110096		\N	0bef612b-0edf-4c3a-9fba-00c6ca40b6d6	2026-04-25 11:17:11.573312+00	2026-04-25 11:17:11.825628+00	https://ecommerce.vidharthigeneralstore.in/uploads/pdfs/invoice_0bef612b-0edf-4c3a-9fba-00c6ca40b6d6.pdf	https://ecommerce.vidharthigeneralstore.in/uploads/pdfs/shipping_label_0bef612b-0edf-4c3a-9fba-00c6ca40b6d6.pdf	INV-2026-0002
9bf932ac-f606-41ed-9aa5-333eed1a84c3	placed	39.00	30.00	69.00	B-180, new ashok nagar, New delhi, Delhi - 110096		\N	154be291-f31d-45f1-b03f-2170de980f93	2026-04-26 05:22:24.069353+00	2026-04-26 05:22:26.180622+00	https://ecommerce.vidharthigeneralstore.in/uploads/pdfs/invoice_154be291-f31d-45f1-b03f-2170de980f93.pdf	https://ecommerce.vidharthigeneralstore.in/uploads/pdfs/shipping_label_154be291-f31d-45f1-b03f-2170de980f93.pdf	INV-2026-0003
9bf932ac-f606-41ed-9aa5-333eed1a84c3	placed	30.00	30.00	60.00	B-180, new ashok nagar, New delhi, Delhi - 110096		\N	6bbde858-c1d1-4cba-9699-2f92763e9ddb	2026-04-26 09:12:16.267164+00	2026-04-26 09:19:34.90206+00	http://localhost:8000/uploads/pdfs/invoice_6bbde858-c1d1-4cba-9699-2f92763e9ddb.pdf	http://localhost:8000/uploads/pdfs/shipping_label_6bbde858-c1d1-4cba-9699-2f92763e9ddb.pdf	INV-2026-0004
\.


--
-- TOC entry 4569 (class 0 OID 18104)
-- Dependencies: 232
-- Data for Name: otps; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."otps" ("user_id", "code", "is_used", "expires_at", "id", "created_at", "updated_at") FROM stdin;
81c6f7c3-b029-40de-ac9f-1a9de870ffb7	702762	t	2026-04-25T09:41:49.631777+00:00	5bff9f90-ece2-4c63-bd20-26fddcb5c8d2	2026-04-25 09:31:49.618299+00	2026-04-25 09:32:19.634248+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	978615	t	2026-04-25T10:02:04.327344+00:00	0a86742d-adbb-4c1b-8514-76bab97ff631	2026-04-25 09:52:04.320864+00	2026-04-25 09:52:48.134059+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	239012	t	2026-04-25T18:04:19.930862+00:00	76797141-7b56-44b9-bec9-9dec2545f29c	2026-04-25 17:54:19.921195+00	2026-04-25 17:54:45.242251+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	036610	t	2026-04-25T19:29:07.341230+00:00	cd836a20-db01-401d-9255-820dc307e7f4	2026-04-25 19:19:07.333621+00	2026-04-25 19:19:41.347762+00
81c6f7c3-b029-40de-ac9f-1a9de870ffb7	589688	t	2026-04-26T07:41:26.994085+00:00	23809c4c-8aa9-4f1a-beb9-95994f588c08	2026-04-26 07:31:26.984293+00	2026-04-26 07:32:07.59911+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	838860	t	2026-04-26T08:46:16.654036+00:00	7235b001-5f1a-456b-9b13-48ff558af5e0	2026-04-26 08:36:16.644687+00	2026-04-26 08:53:29.311139+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	184251	t	2026-04-26T09:03:30.468220+00:00	2f820557-6011-49c7-9dd6-08b8c76e89a7	2026-04-26 08:53:29.311139+00	2026-04-26 09:10:35.150934+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	030799	t	2026-04-26T09:20:36.240102+00:00	1dd97cb4-4d76-4938-88bb-2293856cdab0	2026-04-26 09:10:35.150934+00	2026-04-26 09:11:25.494138+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	343529	t	2026-04-26T09:21:26.701267+00:00	18ed8ad9-d582-4bb2-84ce-995bb621f9a0	2026-04-26 09:11:25.494138+00	2026-04-26 09:11:44.391988+00
9bf932ac-f606-41ed-9aa5-333eed1a84c3	652319	t	2026-04-26T09:35:23.357322+00:00	53da4af7-a464-4201-8f64-e4af5aca42bd	2026-04-26 09:25:22.153988+00	2026-04-26 09:25:50.180598+00
\.


--
-- TOC entry 4570 (class 0 OID 18119)
-- Dependencies: 233
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."products" ("name", "description", "price", "mrp", "stock", "unit", "image_url", "is_active", "is_out_of_stock", "category_id", "id", "created_at", "updated_at", "is_deleted", "name_hi", "description_hi", "hsn_code", "gst_rate") FROM stdin;
Aeroplane Shudh Chakki Atta| 10 Kg	Aeroplane, a brand that you love and trust, ensures that good quality products reach your kitchen hence it brings to you a range of products that are certified by leading product bodies. Aeroplane Shudh Chakki Atta adheres to stringent quality checks and product norms. It has been expertly sourced and hygienically packed to give you both, taste, and nutrition. This whole wheat atta has natural dietary fibres and nutrients. It helps in easy digestion and supports immunity which is essential for you and your family’s daily intake. So, enjoy a healthy and sustainable lifestyle as you indulge in soft and tasty Rotis with Aeroplane 100%  wheat atta. So, switch to Aeroplane atta and take one step forward towards a sustainable way of life.	479.00	650.00	39	piece	https://ecommerce.vidharthigeneralstore.in/uploads/products/016cb534c315425a9a1e422dea2d2525.webp	t	f	0f3cf1c1-769d-4561-a34f-4b66276fc798	359841ea-902c-40b4-8a86-006fcb45f091	2026-04-25 08:51:56.160783+00	2026-04-25 08:53:10.138396+00	f	\N	\N	\N	\N
Fresh Onion, 1kg	\N	28.00	40.00	30	piece	https://ecommerce.vidharthigeneralstore.in/uploads/products/d267b80abfc64605a9d29c33ffe51bcd.jpg	t	f	893a2be3-24a0-4eb7-a121-3e686a48a217	27307022-6b56-49b5-a01a-23011dd7448f	2026-04-25 09:09:11.928799+00	2026-04-25 09:09:11.928799+00	f	\N	\N	\N	\N
Fresh Bhendi (Lady Finger), 500g	\N	31.00	50.00	29	piece	https://ecommerce.vidharthigeneralstore.in/uploads/products/b55a532746dc4ceaa9f7573f49b78f6b.jpg	t	f	893a2be3-24a0-4eb7-a121-3e686a48a217	c885788e-3df5-4ea3-b21d-a37c1b4d5050	2026-04-25 09:07:51.752814+00	2026-04-25 11:17:11.573312+00	f	\N	\N	\N	\N
Fresh Organic Tendli, 250 g	\N	39.00	50.00	49	piece	https://ecommerce.vidharthigeneralstore.in/uploads/products/8c5965e7fab84289b75d97c6b6590e58.jpg	t	f	893a2be3-24a0-4eb7-a121-3e686a48a217	b7ea41dc-bbb8-46a0-aa20-7df8f62245fd	2026-04-25 09:10:18.164433+00	2026-04-26 05:22:24.069353+00	f	\N	\N	\N	\N
Fresh Tomato - Local, 1kg	\N	30.00	46.00	49	piece	https://ecommerce.vidharthigeneralstore.in/uploads/products/09f2ecfd03704aa5a01c603d1c526e80.jpg	t	f	893a2be3-24a0-4eb7-a121-3e686a48a217	9467ea61-4561-4d03-beba-cc2581da9287	2026-04-25 09:11:35.055651+00	2026-04-26 09:12:16.267164+00	f	\N	\N	\N	\N
\.


--
-- TOC entry 4571 (class 0 OID 18141)
-- Dependencies: 234
-- Data for Name: uploaded_files; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."uploaded_files" ("original_filename", "file_path", "file_url", "file_size", "mime_type", "entity_type", "entity_id", "uploaded_by", "id", "created_at", "updated_at") FROM stdin;
atta-flours-sooji-20240621.webp	uploads/categories/519c585670514514808f1dab1c3118f6.webp	uploads/categories/519c585670514514808f1dab1c3118f6.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	e2807846-7d43-4852-ac5f-a63cb459b6a3	2026-04-25 08:21:27.066848+00	2026-04-25 08:21:27.066848+00
atta-flours-sooji-20240621.webp	uploads/categories/208de506be7a4b6bb082f3dc5b5473c4.webp	uploads/categories/208de506be7a4b6bb082f3dc5b5473c4.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	ceedabe0-6b42-4ed8-aac1-73c75071efe7	2026-04-25 08:22:05.400098+00	2026-04-25 08:22:05.400098+00
aero-atta_10kg-product-images-orvsztom8qj-p596875708-0-202301022029.webp	uploads/products/905c7cacba23425fb53f6914527d79bc.webp	uploads/products/905c7cacba23425fb53f6914527d79bc.webp	14112	image/webp	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	2cb895bf-06b9-4f1d-872f-b30710f1c4e5	2026-04-25 08:25:23.967729+00	2026-04-25 08:25:23.967729+00
fenugreek-home-deliveryMethi.png	uploads/products/9ca0967fc1834c939c2226f01278feb5.png	uploads/products/9ca0967fc1834c939c2226f01278feb5.png	301376	image/png	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	be4a47c1-e9bb-4ee3-9f26-56fcf79a4820	2026-04-25 08:30:09.614667+00	2026-04-25 08:30:09.614667+00
4254fe618ceb46f79bc291ef0fca7fea.webp	uploads/categories/b5864e0e2f094a6caa334f3be60c033c.webp	uploads/categories/b5864e0e2f094a6caa334f3be60c033c.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	f7ce6f07-d909-4c85-9afc-60f7b84a355c	2026-04-25 08:30:40.236405+00	2026-04-25 08:30:40.236405+00
4254fe618ceb46f79bc291ef0fca7fea.webp	uploads/categories/d3175e79a2434dd99c3370481e3ce874.webp	uploads/categories/d3175e79a2434dd99c3370481e3ce874.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	b41892df-9c19-41c2-bc1f-d4e525e01e24	2026-04-25 08:31:31.455987+00	2026-04-25 08:31:31.455987+00
buy-ghevda-online-in-pune.png	uploads/products/fbec4a3fd7ce41d29ee532e7b28a0483.png	uploads/products/fbec4a3fd7ce41d29ee532e7b28a0483.png	270198	image/png	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	2a8318f0-37ec-4cea-88e7-0427c0175366	2026-04-25 08:31:34.353816+00	2026-04-25 08:31:34.353816+00
atta-flours-sooji-20240621.webp	uploads/products/e936f7fa07734ffcbd8ea53ce9353962.webp	uploads/products/e936f7fa07734ffcbd8ea53ce9353962.webp	12500	image/webp	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	680c83a5-3da9-4147-bea9-0c2372ceff29	2026-04-25 08:41:28.557299+00	2026-04-25 08:41:28.557299+00
atta-flours-sooji-20240621.webp	uploads/categories/6c184678de0b483e9e8e6fd0735fb1c5.webp	uploads/categories/6c184678de0b483e9e8e6fd0735fb1c5.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	202cb999-a6b9-4405-8e54-e609cf53923e	2026-04-25 08:41:57.68312+00	2026-04-25 08:41:57.68312+00
atta-flours-sooji-20240621.webp	uploads/categories/fe07252b93e548adb32fbea0f75bdba2.webp	uploads/categories/fe07252b93e548adb32fbea0f75bdba2.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	070a3de1-af2c-439c-a4be-07525b0c8e32	2026-04-25 08:42:24.667001+00	2026-04-25 08:42:24.667001+00
atta-flours-sooji-20240621.webp	uploads/categories/46153a79c5434ea1a8fab74c6fb07cfe.webp	uploads/categories/46153a79c5434ea1a8fab74c6fb07cfe.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	f3837fa1-f76e-4807-9e2a-498ccbf80556	2026-04-25 08:46:38.986636+00	2026-04-25 08:46:38.986636+00
atta-flours-sooji-20240621.webp	uploads/categories/1931644274f54c3f8efd92f7ea710214.webp	uploads/categories/1931644274f54c3f8efd92f7ea710214.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	4d0cac36-9087-4799-b8d8-d3191cb8dbf2	2026-04-25 08:46:55.252615+00	2026-04-25 08:46:55.252615+00
b5864e0e2f094a6caa334f3be60c033c.webp	uploads/categories/e610310cc2034ddcbb20a1851feec96f.webp	uploads/categories/e610310cc2034ddcbb20a1851feec96f.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	cc631e49-4ab0-4c45-9c33-a9dcd5e5bc8a	2026-04-25 08:50:51.522455+00	2026-04-25 08:50:51.522455+00
atta-flours-sooji-20240621.webp	uploads/categories/d39283234da64f4ca17f4ac9df06644a.webp	uploads/categories/d39283234da64f4ca17f4ac9df06644a.webp	12500	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	f9807152-6675-4f2a-8af1-e26cb9cf4d47	2026-04-25 08:50:53.634452+00	2026-04-25 08:50:53.634452+00
aero-atta_10kg-product-images-orvsztom8qj-p596875708-0-202301022029.webp	uploads/products/016cb534c315425a9a1e422dea2d2525.webp	uploads/products/016cb534c315425a9a1e422dea2d2525.webp	14112	image/webp	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	f3eb1195-ee46-4381-acdc-e613d613db2d	2026-04-25 08:51:54.789554+00	2026-04-25 08:51:54.789554+00
dals-pulses-20250617.webp	uploads/categories/76d4e67ac33a4cdfa91fad2010218681.webp	uploads/categories/76d4e67ac33a4cdfa91fad2010218681.webp	9034	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	8241c145-d4d9-463a-98b6-90dcc5747cf0	2026-04-25 08:56:41.376532+00	2026-04-25 08:56:41.376532+00
rice-20250708.webp	uploads/categories/51047edfa1844f719f1664daf5c624f5.webp	uploads/categories/51047edfa1844f719f1664daf5c624f5.webp	8808	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	00f50b54-7671-4854-9f69-2f70f1b7bbd1	2026-04-25 08:57:12.339503+00	2026-04-25 08:57:12.339503+00
salt-sugar-jaggery-20260105.webp	uploads/categories/492301166dba4b4caef63e7830227b60.webp	uploads/categories/492301166dba4b4caef63e7830227b60.webp	9360	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	60dfa692-2208-467b-b360-b7f73731226f	2026-04-25 08:58:11.016514+00	2026-04-25 08:58:11.016514+00
edible-oils-20240621.webp	uploads/categories/a2c48066d8f9401db9cca9ddc7eebb95.webp	uploads/categories/a2c48066d8f9401db9cca9ddc7eebb95.webp	9418	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	0a0eb12c-9648-4e7a-9b89-3001fdcf9001	2026-04-25 09:00:18.316069+00	2026-04-25 09:00:18.316069+00
masala-spices-mukhwas-20251030.webp	uploads/categories/b13c63379b1547649c9e6756c938bbc0.webp	uploads/categories/b13c63379b1547649c9e6756c938bbc0.webp	7168	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	e890cc1d-63c1-4af7-9bf5-9a97371b5fe6	2026-04-25 09:01:06.097505+00	2026-04-25 09:01:06.097505+00
wheat-soya-20240621.webp	uploads/categories/10cd5b49f9b34522a76bb0d3840afa4c.webp	uploads/categories/10cd5b49f9b34522a76bb0d3840afa4c.webp	13164	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	5c1e4e95-02a7-48dd-8f4a-7af8895b8169	2026-04-25 09:01:52.433625+00	2026-04-25 09:01:52.433625+00
dry-fruits-nuts-20240617.png	uploads/categories/cfd1bef55eb443188b01a524b58367be.png	uploads/categories/cfd1bef55eb443188b01a524b58367be.png	47072	image/png	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	4c1a1356-c18f-4d2e-90a3-663fccffaa1d	2026-04-25 09:02:26.203484+00	2026-04-25 09:02:26.203484+00
51yvxGKCiYL._SL1100_.jpg	uploads/products/b55a532746dc4ceaa9f7573f49b78f6b.jpg	uploads/products/b55a532746dc4ceaa9f7573f49b78f6b.jpg	48880	image/jpeg	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	81e564f5-ac33-43bb-8e5f-850a1caf6217	2026-04-25 09:07:50.14684+00	2026-04-25 09:07:50.14684+00
51DJ-9xkuQL._SL1000_.jpg	uploads/products/d267b80abfc64605a9d29c33ffe51bcd.jpg	uploads/products/d267b80abfc64605a9d29c33ffe51bcd.jpg	56190	image/jpeg	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	c68b6d8f-4f54-4813-92aa-ca4a4e9ac797	2026-04-25 09:09:09.911236+00	2026-04-25 09:09:09.911236+00
91zGB7KyBlL._SL1500_.jpg	uploads/products/8c5965e7fab84289b75d97c6b6590e58.jpg	uploads/products/8c5965e7fab84289b75d97c6b6590e58.jpg	151613	image/jpeg	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	059b0715-8973-4719-b81f-b0a14a0b648f	2026-04-25 09:10:16.653634+00	2026-04-25 09:10:16.653634+00
61ZJhcdG7LL._SL1500_.jpg	uploads/products/09f2ecfd03704aa5a01c603d1c526e80.jpg	uploads/products/09f2ecfd03704aa5a01c603d1c526e80.jpg	101130	image/jpeg	product	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	c7921927-9322-4736-8aab-7a9afc888433	2026-04-25 09:11:30.383731+00	2026-04-25 09:11:30.383731+00
rice-20250708.webp	uploads/categories/a17bc7b9ef954286b3314255ac046f55.webp	uploads/categories/a17bc7b9ef954286b3314255ac046f55.webp	8808	image/webp	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	46495202-194b-4061-8695-d9e39196622c	2026-04-25 12:06:47.519159+00	2026-04-25 12:06:47.519159+00
pngtree-grocery-basket-and-a-list-of-products-png-image_14956705.png	uploads/categories/9ba0fd37d5f94128b33ecce1fc344304.png	uploads/categories/9ba0fd37d5f94128b33ecce1fc344304.png	450318	image/png	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	e5439cf3-b767-4855-adc6-21ef5d9fd2dd	2026-04-25 12:07:59.969292+00	2026-04-25 12:07:59.969292+00
—Pngtree—vibrant-fresh-vegetables-clipart-set_19241377.png	uploads/categories/792dfaf5501240578eb09a3dbf900cfb.png	uploads/categories/792dfaf5501240578eb09a3dbf900cfb.png	307632	image/png	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	2b75765b-af48-44c0-a070-25c731384f58	2026-04-25 12:11:11.096212+00	2026-04-25 12:11:11.096212+00
cfd1bef55eb443188b01a524b58367be.png	uploads/categories/4d9ccabd133f414f8c26740602541d81.png	uploads/categories/4d9ccabd133f414f8c26740602541d81.png	47072	image/png	category	\N	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	a0e7db9e-edbc-4772-9b43-bfa4bb432598	2026-04-26 07:37:29.103663+00	2026-04-26 07:37:29.103663+00
\.


--
-- TOC entry 4572 (class 0 OID 18157)
-- Dependencies: 235
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."users" ("full_name", "email", "phone", "hashed_password", "avatar_url", "is_active", "is_verified", "is_admin", "id", "created_at", "updated_at", "is_super_admin", "is_deleted", "deleted_at") FROM stdin;
Super Admin	superadmin@vidharthi.com	9999999990	$2b$12$msHS8JhWJl5WilgC8El7D.yEaVJ/w4nSNHHM1KnSIQP0sg3GXhc/.	\N	t	t	t	37360e76-c255-46f4-9b68-5bc21a3b5ac8	2026-04-21 15:14:25.871384+00	2026-04-21 15:14:25.871384+00	t	f	\N
Admin User	admin@vidharthi.com	9999999999	$2b$12$NYb/LuiJwYooMMmAvwWfNOM/CPf1VzU9wGFywU47d65/mmS6Ao7fy	\N	t	t	t	7d01fafc-10e4-4d81-8c2e-12b29eb2cbbb	2026-04-21 15:14:25.12712+00	2026-04-21 15:14:25.12712+00	f	f	\N
Pravin Kumar	kumar.pravin160@gmail.com	9971411966	$2b$12$6kzb3MtvWp89Vl2bPAIObOywc5q4c8xcm/aZaEiu/qxBgq5It.yLi	\N	t	t	f	81c6f7c3-b029-40de-ac9f-1a9de870ffb7	2026-04-25 06:46:34.73559+00	2026-04-25 09:32:19.634248+00	f	f	\N
sanjay kumar chaudhary	chaudharysanjay699@gmail.com	7000000000	$2b$12$1aXPw5JcS2yDPA.AmdaT1u6MACJUMX7TMh6u8iQD7K2m8zzW6EOHi	\N	t	t	f	9bf932ac-f606-41ed-9aa5-333eed1a84c3	2026-04-25 08:03:56.943886+00	2026-04-25 09:52:48.134059+00	f	f	\N
Omnath kumar	sunil4252kumar@gmail.com	6204273313	$2b$12$ewoI1vsCJJsm9OCIEadvpeYPYBxF8FetrZ6nMVxjHHrTSxMMvmAhy	\N	t	f	f	4bba9ed9-7f55-4d34-b828-d81565054406	2026-04-26 06:12:27.230789+00	2026-04-26 06:12:27.230789+00	f	f	\N
\.


--
-- TOC entry 4573 (class 0 OID 18179)
-- Dependencies: 236
-- Data for Name: wishlist_items; Type: TABLE DATA; Schema: public; Owner: -
--

COPY "public"."wishlist_items" ("id", "user_id", "product_id", "created_at", "updated_at") FROM stdin;
ea46faa7-c4a3-431d-87ea-263088487b80	81c6f7c3-b029-40de-ac9f-1a9de870ffb7	b7ea41dc-bbb8-46a0-aa20-7df8f62245fd	2026-04-25 09:12:04.811051+00	2026-04-25 09:12:04.811051+00
\.


--
-- TOC entry 4312 (class 2606 OID 18190)
-- Name: addresses addresses_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."addresses"
    ADD CONSTRAINT "addresses_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4316 (class 2606 OID 18192)
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."alembic_version"
    ADD CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num");


--
-- TOC entry 4318 (class 2606 OID 18194)
-- Name: app_settings app_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."app_settings"
    ADD CONSTRAINT "app_settings_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4320 (class 2606 OID 18196)
-- Name: banners banners_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."banners"
    ADD CONSTRAINT "banners_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4323 (class 2606 OID 18198)
-- Name: cart_items cart_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."cart_items"
    ADD CONSTRAINT "cart_items_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4330 (class 2606 OID 18200)
-- Name: carts carts_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."carts"
    ADD CONSTRAINT "carts_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4334 (class 2606 OID 18202)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "categories_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4339 (class 2606 OID 18204)
-- Name: device_tokens device_tokens_device_token_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."device_tokens"
    ADD CONSTRAINT "device_tokens_device_token_key" UNIQUE ("device_token");


--
-- TOC entry 4341 (class 2606 OID 18206)
-- Name: device_tokens device_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."device_tokens"
    ADD CONSTRAINT "device_tokens_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4348 (class 2606 OID 18208)
-- Name: notifications notifications_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."notifications"
    ADD CONSTRAINT "notifications_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4352 (class 2606 OID 18210)
-- Name: offers offers_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."offers"
    ADD CONSTRAINT "offers_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4357 (class 2606 OID 18212)
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."order_items"
    ADD CONSTRAINT "order_items_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4361 (class 2606 OID 18214)
-- Name: order_tracking order_tracking_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."order_tracking"
    ADD CONSTRAINT "order_tracking_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4366 (class 2606 OID 18216)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."orders"
    ADD CONSTRAINT "orders_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4370 (class 2606 OID 18218)
-- Name: otps otps_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."otps"
    ADD CONSTRAINT "otps_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4374 (class 2606 OID 18220)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."products"
    ADD CONSTRAINT "products_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4378 (class 2606 OID 18222)
-- Name: uploaded_files uploaded_files_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."uploaded_files"
    ADD CONSTRAINT "uploaded_files_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4328 (class 2606 OID 18224)
-- Name: cart_items uq_cart_product; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."cart_items"
    ADD CONSTRAINT "uq_cart_product" UNIQUE ("cart_id", "product_id");


--
-- TOC entry 4388 (class 2606 OID 18226)
-- Name: wishlist_items uq_wishlist_user_product; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."wishlist_items"
    ADD CONSTRAINT "uq_wishlist_user_product" UNIQUE ("user_id", "product_id");


--
-- TOC entry 4383 (class 2606 OID 18228)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."users"
    ADD CONSTRAINT "users_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4390 (class 2606 OID 18230)
-- Name: wishlist_items wishlist_items_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."wishlist_items"
    ADD CONSTRAINT "wishlist_items_pkey" PRIMARY KEY ("id");


--
-- TOC entry 4313 (class 1259 OID 18231)
-- Name: ix_addresses_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_addresses_id" ON "public"."addresses" USING "btree" ("id");


--
-- TOC entry 4314 (class 1259 OID 18232)
-- Name: ix_addresses_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_addresses_user_id" ON "public"."addresses" USING "btree" ("user_id");


--
-- TOC entry 4321 (class 1259 OID 18233)
-- Name: ix_banners_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_banners_id" ON "public"."banners" USING "btree" ("id");


--
-- TOC entry 4324 (class 1259 OID 18234)
-- Name: ix_cart_items_cart_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_cart_items_cart_id" ON "public"."cart_items" USING "btree" ("cart_id");


--
-- TOC entry 4325 (class 1259 OID 18235)
-- Name: ix_cart_items_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_cart_items_id" ON "public"."cart_items" USING "btree" ("id");


--
-- TOC entry 4326 (class 1259 OID 18236)
-- Name: ix_cart_items_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_cart_items_product_id" ON "public"."cart_items" USING "btree" ("product_id");


--
-- TOC entry 4331 (class 1259 OID 18237)
-- Name: ix_carts_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_carts_id" ON "public"."carts" USING "btree" ("id");


--
-- TOC entry 4332 (class 1259 OID 18238)
-- Name: ix_carts_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_carts_user_id" ON "public"."carts" USING "btree" ("user_id");


--
-- TOC entry 4335 (class 1259 OID 18239)
-- Name: ix_categories_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_categories_id" ON "public"."categories" USING "btree" ("id");


--
-- TOC entry 4336 (class 1259 OID 18240)
-- Name: ix_categories_parent_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_categories_parent_id" ON "public"."categories" USING "btree" ("parent_id");


--
-- TOC entry 4337 (class 1259 OID 18241)
-- Name: ix_categories_slug; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_categories_slug" ON "public"."categories" USING "btree" ("slug");


--
-- TOC entry 4342 (class 1259 OID 18242)
-- Name: ix_device_tokens_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_device_tokens_id" ON "public"."device_tokens" USING "btree" ("id");


--
-- TOC entry 4343 (class 1259 OID 18243)
-- Name: ix_device_tokens_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_device_tokens_user_id" ON "public"."device_tokens" USING "btree" ("user_id");


--
-- TOC entry 4344 (class 1259 OID 18244)
-- Name: ix_notifications_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_notifications_id" ON "public"."notifications" USING "btree" ("id");


--
-- TOC entry 4345 (class 1259 OID 18245)
-- Name: ix_notifications_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_notifications_order_id" ON "public"."notifications" USING "btree" ("order_id");


--
-- TOC entry 4346 (class 1259 OID 18246)
-- Name: ix_notifications_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_notifications_user_id" ON "public"."notifications" USING "btree" ("user_id");


--
-- TOC entry 4349 (class 1259 OID 18247)
-- Name: ix_offers_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_offers_id" ON "public"."offers" USING "btree" ("id");


--
-- TOC entry 4350 (class 1259 OID 18248)
-- Name: ix_offers_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_offers_product_id" ON "public"."offers" USING "btree" ("product_id");


--
-- TOC entry 4353 (class 1259 OID 18249)
-- Name: ix_order_items_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_order_items_id" ON "public"."order_items" USING "btree" ("id");


--
-- TOC entry 4354 (class 1259 OID 18250)
-- Name: ix_order_items_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_order_items_order_id" ON "public"."order_items" USING "btree" ("order_id");


--
-- TOC entry 4355 (class 1259 OID 18251)
-- Name: ix_order_items_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_order_items_product_id" ON "public"."order_items" USING "btree" ("product_id");


--
-- TOC entry 4358 (class 1259 OID 18252)
-- Name: ix_order_tracking_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_order_tracking_id" ON "public"."order_tracking" USING "btree" ("id");


--
-- TOC entry 4359 (class 1259 OID 18253)
-- Name: ix_order_tracking_order_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_order_tracking_order_id" ON "public"."order_tracking" USING "btree" ("order_id");


--
-- TOC entry 4362 (class 1259 OID 18254)
-- Name: ix_orders_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_orders_id" ON "public"."orders" USING "btree" ("id");


--
-- TOC entry 4363 (class 1259 OID 18255)
-- Name: ix_orders_invoice_number; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "ix_orders_invoice_number" ON "public"."orders" USING "btree" ("invoice_number");


--
-- TOC entry 4364 (class 1259 OID 18256)
-- Name: ix_orders_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_orders_user_id" ON "public"."orders" USING "btree" ("user_id");


--
-- TOC entry 4367 (class 1259 OID 18257)
-- Name: ix_otps_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_otps_id" ON "public"."otps" USING "btree" ("id");


--
-- TOC entry 4368 (class 1259 OID 18258)
-- Name: ix_otps_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_otps_user_id" ON "public"."otps" USING "btree" ("user_id");


--
-- TOC entry 4371 (class 1259 OID 18259)
-- Name: ix_products_category_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_products_category_id" ON "public"."products" USING "btree" ("category_id");


--
-- TOC entry 4372 (class 1259 OID 18260)
-- Name: ix_products_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_products_id" ON "public"."products" USING "btree" ("id");


--
-- TOC entry 4375 (class 1259 OID 18261)
-- Name: ix_uploaded_files_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_uploaded_files_id" ON "public"."uploaded_files" USING "btree" ("id");


--
-- TOC entry 4376 (class 1259 OID 18262)
-- Name: ix_uploaded_files_uploaded_by; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_uploaded_files_uploaded_by" ON "public"."uploaded_files" USING "btree" ("uploaded_by");


--
-- TOC entry 4379 (class 1259 OID 18263)
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_users_id" ON "public"."users" USING "btree" ("id");


--
-- TOC entry 4384 (class 1259 OID 18264)
-- Name: ix_wishlist_items_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_wishlist_items_id" ON "public"."wishlist_items" USING "btree" ("id");


--
-- TOC entry 4385 (class 1259 OID 18265)
-- Name: ix_wishlist_items_product_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_wishlist_items_product_id" ON "public"."wishlist_items" USING "btree" ("product_id");


--
-- TOC entry 4386 (class 1259 OID 18266)
-- Name: ix_wishlist_items_user_id; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX "ix_wishlist_items_user_id" ON "public"."wishlist_items" USING "btree" ("user_id");


--
-- TOC entry 4380 (class 1259 OID 18267)
-- Name: uq_users_email_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "uq_users_email_active" ON "public"."users" USING "btree" ("email") WHERE (("is_deleted" = false) AND ("email" IS NOT NULL));


--
-- TOC entry 4381 (class 1259 OID 18268)
-- Name: uq_users_phone_active; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX "uq_users_phone_active" ON "public"."users" USING "btree" ("phone") WHERE ("is_deleted" = false);


--
-- TOC entry 4391 (class 2606 OID 18269)
-- Name: addresses addresses_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."addresses"
    ADD CONSTRAINT "addresses_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4392 (class 2606 OID 18274)
-- Name: cart_items cart_items_cart_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."cart_items"
    ADD CONSTRAINT "cart_items_cart_id_fkey" FOREIGN KEY ("cart_id") REFERENCES "public"."carts"("id") ON DELETE CASCADE;


--
-- TOC entry 4393 (class 2606 OID 18279)
-- Name: cart_items cart_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."cart_items"
    ADD CONSTRAINT "cart_items_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "public"."products"("id") ON DELETE CASCADE;


--
-- TOC entry 4394 (class 2606 OID 18284)
-- Name: carts carts_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."carts"
    ADD CONSTRAINT "carts_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4396 (class 2606 OID 18289)
-- Name: device_tokens device_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."device_tokens"
    ADD CONSTRAINT "device_tokens_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4395 (class 2606 OID 18294)
-- Name: categories fk_categories_parent_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."categories"
    ADD CONSTRAINT "fk_categories_parent_id" FOREIGN KEY ("parent_id") REFERENCES "public"."categories"("id") ON DELETE SET NULL;


--
-- TOC entry 4397 (class 2606 OID 18299)
-- Name: notifications fk_notifications_order_id; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."notifications"
    ADD CONSTRAINT "fk_notifications_order_id" FOREIGN KEY ("order_id") REFERENCES "public"."orders"("id") ON DELETE SET NULL;


--
-- TOC entry 4398 (class 2606 OID 18304)
-- Name: notifications notifications_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."notifications"
    ADD CONSTRAINT "notifications_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4399 (class 2606 OID 18309)
-- Name: offers offers_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."offers"
    ADD CONSTRAINT "offers_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "public"."products"("id") ON DELETE CASCADE;


--
-- TOC entry 4400 (class 2606 OID 18314)
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."order_items"
    ADD CONSTRAINT "order_items_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "public"."orders"("id") ON DELETE CASCADE;


--
-- TOC entry 4401 (class 2606 OID 18319)
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."order_items"
    ADD CONSTRAINT "order_items_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "public"."products"("id") ON DELETE RESTRICT;


--
-- TOC entry 4402 (class 2606 OID 18324)
-- Name: order_tracking order_tracking_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."order_tracking"
    ADD CONSTRAINT "order_tracking_order_id_fkey" FOREIGN KEY ("order_id") REFERENCES "public"."orders"("id") ON DELETE CASCADE;


--
-- TOC entry 4403 (class 2606 OID 18329)
-- Name: orders orders_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."orders"
    ADD CONSTRAINT "orders_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE RESTRICT;


--
-- TOC entry 4404 (class 2606 OID 18334)
-- Name: otps otps_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."otps"
    ADD CONSTRAINT "otps_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;


--
-- TOC entry 4405 (class 2606 OID 18339)
-- Name: products products_category_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."products"
    ADD CONSTRAINT "products_category_id_fkey" FOREIGN KEY ("category_id") REFERENCES "public"."categories"("id") ON DELETE RESTRICT;


--
-- TOC entry 4406 (class 2606 OID 18344)
-- Name: uploaded_files uploaded_files_uploaded_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."uploaded_files"
    ADD CONSTRAINT "uploaded_files_uploaded_by_fkey" FOREIGN KEY ("uploaded_by") REFERENCES "public"."users"("id") ON DELETE SET NULL;


--
-- TOC entry 4407 (class 2606 OID 18349)
-- Name: wishlist_items wishlist_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."wishlist_items"
    ADD CONSTRAINT "wishlist_items_product_id_fkey" FOREIGN KEY ("product_id") REFERENCES "public"."products"("id") ON DELETE CASCADE;


--
-- TOC entry 4408 (class 2606 OID 18354)
-- Name: wishlist_items wishlist_items_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY "public"."wishlist_items"
    ADD CONSTRAINT "wishlist_items_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."users"("id") ON DELETE CASCADE;


-- Completed on 2026-04-26 15:24:25

--
-- PostgreSQL database dump complete
--

\unrestrict gKxxUpr1nv91UTJn6Q9epVoww3TIicKDsXg1DPjQjoBfJ1OfzUEWY3vBsKiU9GL

