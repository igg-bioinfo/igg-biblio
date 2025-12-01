-- public.pubmed_pubs definition

-- Drop table

-- DROP TABLE public.pubmed_pubs;

CREATE TABLE public.pubmed_pubs (
	pub_authors int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	doi varchar NULL,
	pm_id varchar NOT NULL,
	title varchar NULL,
	pub_date varchar NOT NULL,
	pmc_id varchar NULL,
	journal varchar NOT NULL,
	issn varchar NOT NULL,
	author_orcid varchar NULL,
	author_name varchar NOT NULL,
	is_person bool NOT NULL,
	"position" varchar NOT NULL,
	"corresponding" bool NULL,
	affiliations jsonb NOT NULL,
	update_date date NOT NULL,
	update_year int4 NOT NULL,
	CONSTRAINT pubmed_pubs_pk PRIMARY KEY (pub_authors)
);