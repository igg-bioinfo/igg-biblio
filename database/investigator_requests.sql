-- public.investigator_requests definition

-- Drop table

-- DROP TABLE public.investigator_requests;

CREATE TABLE public.investigator_requests (
	email varchar NOT NULL,
	first_name varchar NULL,
	last_name varchar NULL,
	contract varchar NULL,
	unit varchar NULL,
	scopus_id varchar NULL,
	orcid_id varchar NULL,
	researcher_id varchar NULL,
	update_date date NOT NULL,
	status int4 NOT NULL
);