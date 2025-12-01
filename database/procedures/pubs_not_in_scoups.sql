-- DROP FUNCTION public.pubs_not_in_scopus(int4);

CREATE OR REPLACE FUNCTION public.pubs_not_in_scopus(pub_year integer)
 RETURNS TABLE(doi character varying, pm_id character varying, title character varying, pub_date character varying, pmc_id character varying, journal character varying, issn character varying)
 LANGUAGE plpgsql
AS $function$
begin
    RETURN QUERY
	select distinct pp.doi, pp.pm_id, pp.title, pp.pub_date, pp.pmc_id, pp.journal, pp.issn 
	from pubmed_pubs pp 
	where EXTRACT('Year' from TO_DATE(pp.pub_date,'YYYY-MM-DD')) = pub_year
	and pp.pm_id not in (
		select distinct spa.pm_id
		from scopus_pubs_all spa 
		where spa.pm_id is not null and EXTRACT('Year' from TO_DATE(spa.pub_date,'YYYY-MM-DD')) = pub_year
	)
	and pp.doi not in (
		select distinct spa.doi
		from scopus_pubs_all spa 
		where spa.doi is not null and EXTRACT('Year' from TO_DATE(spa.pub_date,'YYYY-MM-DD')) = pub_year
	);
end; $function$
;
