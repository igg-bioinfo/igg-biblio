-- public.users definition

-- Drop table

-- DROP TABLE public.users;

CREATE TABLE public.users (
	user_id int8 GENERATED ALWAYS AS IDENTITY( INCREMENT BY 1 MINVALUE 1 MAXVALUE 9223372036854775807 START 1 CACHE 1 NO CYCLE) NOT NULL,
	user_name varchar NOT NULL,
	user_password varchar NOT NULL,
	user_type varchar NOT NULL,
	"name" varchar NOT NULL,
	is_enabled bool DEFAULT true NOT NULL,
	CONSTRAINT users_pk PRIMARY KEY (user_id)
);
CREATE INDEX users_user_id_idx ON public.users USING btree (user_id);