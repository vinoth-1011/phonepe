--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9 (Debian 16.9-1.pgdg120+1)
-- Dumped by pg_dump version 16.9 (Ubuntu 16.9-0ubuntu0.24.04.1)

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
-- Name: aggregated_insurance_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.aggregated_insurance_data (
    state character varying(100),
    year integer,
    quarter integer,
    transaction_type character varying(100),
    transaction_count bigint,
    transaction_amount numeric(20,2)
);


ALTER TABLE public.aggregated_insurance_data OWNER TO phonepe_m8o9_user;

--
-- Name: aggregated_transaction_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.aggregated_transaction_data (
    state character varying(100),
    year integer,
    quarter integer,
    transaction_type character varying(100),
    transaction_count bigint,
    transaction_amount numeric(20,2)
);


ALTER TABLE public.aggregated_transaction_data OWNER TO phonepe_m8o9_user;

--
-- Name: aggregated_user_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.aggregated_user_data (
    state character varying(100),
    year integer,
    quarter integer,
    brand character varying(100),
    transaction_count bigint,
    transaction_percentage numeric(5,2)
);


ALTER TABLE public.aggregated_user_data OWNER TO phonepe_m8o9_user;

--
-- Name: map_insurance_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.map_insurance_data (
    state character varying(100),
    year integer,
    quarter integer,
    district_state_name character varying(255),
    count bigint,
    amount numeric(20,2)
);


ALTER TABLE public.map_insurance_data OWNER TO phonepe_m8o9_user;

--
-- Name: map_transaction_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.map_transaction_data (
    state character varying(100),
    year integer,
    quarter integer,
    district_state_name character varying(255),
    transaction_count bigint,
    transaction_amount numeric(20,2)
);


ALTER TABLE public.map_transaction_data OWNER TO phonepe_m8o9_user;

--
-- Name: map_user_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.map_user_data (
    state character varying(100),
    year integer,
    quarter integer,
    district_state_name character varying(255),
    registered_users bigint,
    app_opens bigint
);


ALTER TABLE public.map_user_data OWNER TO phonepe_m8o9_user;

--
-- Name: top_insurance_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.top_insurance_data (
    year integer,
    quarter integer,
    state character varying(100),
    entityname character varying(255),
    type character varying(50),
    count bigint,
    amount numeric(20,2)
);


ALTER TABLE public.top_insurance_data OWNER TO phonepe_m8o9_user;

--
-- Name: top_transaction_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.top_transaction_data (
    state character varying(100),
    year integer,
    quarter integer,
    entity_level character varying(50),
    entity_name character varying(255),
    transaction_count bigint,
    transaction_amount numeric(20,2)
);


ALTER TABLE public.top_transaction_data OWNER TO phonepe_m8o9_user;

--
-- Name: top_user_data; Type: TABLE; Schema: public; Owner: phonepe_m8o9_user
--

CREATE TABLE public.top_user_data (
    year integer,
    quarter integer,
    state character varying(100),
    district character varying(255),
    pincode character varying(20),
    registeredusers bigint
);


ALTER TABLE public.top_user_data OWNER TO phonepe_m8o9_user;

--
-- PostgreSQL database dump complete
--

