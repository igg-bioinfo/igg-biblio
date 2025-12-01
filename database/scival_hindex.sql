-- public.scival_hindex definition

-- Drop table

-- DROP TABLE public.scival_hindex;

CREATE TABLE public.scival_hindex (
	metric_id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	author_scopus varchar NOT NULL,
	author_hindex float8 NOT NULL,
	update_date date NULL,
	update_year int4 NULL,
	CONSTRAINT scival_hindex_pk PRIMARY KEY (metric_id)
);