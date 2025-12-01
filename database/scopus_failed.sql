-- public.scopus_failed definition

-- Drop table

-- DROP TABLE public.scopus_failed;

CREATE TABLE public.scopus_failed (
	failed_id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	author_scopus varchar NOT NULL,
	scopus_type varchar NOT NULL,
	update_date date NOT NULL,
	update_year int4 NOT NULL,
	CONSTRAINT scopus_failed_pk PRIMARY KEY (failed_id)
);