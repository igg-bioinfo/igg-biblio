-- public.investigator_details definition

-- Drop table

-- DROP TABLE public.investigator_details;

CREATE TABLE public.investigator_details (
	inv_name varchar NOT NULL,
	scopus_id varchar NULL,
	orcid_id varchar NULL,
	update_date date NOT NULL,
	unit varchar NULL,
	researcher_id varchar NULL,
	contract varchar NULL,
	first_name varchar NULL,
	last_name varchar NULL
);