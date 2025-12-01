-- public.scopus_pucs definition

-- Drop table

-- DROP TABLE public.scopus_pucs;

CREATE TABLE public.scopus_pucs (
	eid varchar NOT NULL,
	first1 varchar NULL,
	first2 varchar NULL,
	first3 varchar NULL,
	last1 varchar NULL,
	last2 varchar NULL,
	last3 varchar NULL,
	corr1 varchar NULL,
	corr2 varchar NULL,
	corr3 varchar NULL,
	corr4 varchar NULL,
	corr5 varchar NULL,
	pub_year int4 NOT NULL,
	CONSTRAINT scopus_pucs_pk PRIMARY KEY (eid)
);