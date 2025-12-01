-- public.scopus_invs definition

-- Drop table

-- DROP TABLE public.scopus_invs;

CREATE TABLE public.scopus_invs (
	scopus_inv_id varchar NOT NULL,
	inv_name varchar NULL,
	inv_surname varchar NULL,
	names jsonb NULL,
	areas jsonb NULL,
	update_date date NOT NULL,
	CONSTRAINT scopus_invs_pk PRIMARY KEY (scopus_inv_id)
);