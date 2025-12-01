-- public.scopus_pubs_all definition

-- Drop table

-- DROP TABLE public.scopus_pubs_all;

CREATE TABLE public.scopus_pubs_all (
	pub_authors int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	doi varchar NULL,
	pm_id varchar NULL,
	title varchar NULL,
	issn varchar NULL,
	author_name varchar NOT NULL,
	author_scopus varchar NOT NULL,
	pub_date varchar NULL,
	pub_type varchar NULL,
	cited int4 NULL,
	update_date date NOT NULL,
	eid varchar NULL,
	pub_status bool NULL,
	CONSTRAINT scopus_pubs_all_pk PRIMARY KEY (pub_authors)
);