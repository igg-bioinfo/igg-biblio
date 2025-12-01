-- DROP FUNCTION public.pubs_missing(int4, varchar);

CREATE OR REPLACE FUNCTION public.pubs_missing(pub_year integer, pub_type character varying)
 RETURNS TABLE(doi character varying, pm_id character varying)
 LANGUAGE plpgsql
AS $function$
declare
dois   character varying(255);
begin
	CREATE TEMP TABLE dois ON COMMIT DROP as (select distinct p.doi from pubs_matching($1) p);
	if $2 = 'scopus' then
        RETURN QUERY
		select distinct t.doi, t.pm_id from pubmed_pubs t where t.update_year = $1 and (t.doi is null or t.doi not in (
			select * from dois
		));
	elsif $2 = 'pubmed' then
        RETURN QUERY
		select distinct t.doi, t.pm_id from scopus_pubs t where t.update_year = $1 and t.doi not in (
			select * from dois
		);
	elsif $2 = 'all' then
        RETURN QUERY
		select distinct * from (
			select distinct t.doi, t.pm_id from pubmed_pubs t where t.update_year = $1 and (t.doi not in (
				select * from dois
			) or t.doi is null)
			union
			select distinct t.doi, t.pm_id from scopus_pubs t where t.update_year = $1 and t.doi not in (
				select * from dois
			)
		) f;
	else
		RAISE NOTICE 'Parametro errato!';
	end if;
end; $function$
;
