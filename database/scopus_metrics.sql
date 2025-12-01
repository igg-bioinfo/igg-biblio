-- public.scopus_metrics definition

-- Drop table

-- DROP TABLE public.scopus_metrics;

CREATE TABLE public.scopus_metrics (
	metric_id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	author_scopus varchar NOT NULL,
	hindex int4 NULL,
	pubs int4 NULL,
	allcited int4 NULL,
	hindex5 int4 NULL,
	pubs5 int4 NULL,
	allcited5 int4 NULL,
	update_date date NOT NULL,
	update_year int4 NOT NULL,
	hindex10 int4 NULL,
	pubs10 int4 NULL,
	allcited10 int4 NULL,
	CONSTRAINT scopus_metrics_pk PRIMARY KEY (metric_id)
);