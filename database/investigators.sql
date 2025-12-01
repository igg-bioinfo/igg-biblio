-- public.investigators definition

-- Drop table

-- DROP TABLE public.investigators;

CREATE TABLE public.investigators (
	inv_id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	inv_name varchar NOT NULL,
	date_birth date NULL,
	contract varchar NULL,
	scopus_id varchar NULL,
	update_date date NOT NULL,
	update_year int4 NOT NULL,
	orcid_id varchar NULL,
	researcher_id varchar NULL,
	unit varchar NULL,
	first_name varchar NULL,
	last_name varchar NULL,
	is_workflow bool DEFAULT true NULL,
	email varchar NULL,
	email2 varchar NULL,
	date_end date NULL,
	CONSTRAINT investigators_pk PRIMARY KEY (inv_id)
);