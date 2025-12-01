-- DROP FUNCTION public.pubs_matching(int4);

CREATE OR REPLACE FUNCTION public.pubs_matching(pub_year integer)
 RETURNS TABLE(doi character varying, pm_id character varying, title character varying)
 LANGUAGE plpgsql
AS $function$
begin
    RETURN QUERY
	select distinct f.doi, 
	case when p.pm_id is null then s.pm_id else p.pm_id end as pm_id, 
	case when p.title is null then s.title else p.title end as title
	from (
		select distinct p.doi from scopus_pubs p where p.update_year = $1 and p.doi in ( 
			select distinct s.doi from pubmed_pubs s where s.doi is not null
		)
		union
		select distinct p.doi from pubmed_pubs p where p.update_year = $1 and p.doi in ( 
			select distinct s.doi from scopus_pubs s where s.doi is not null
		)
	) f 
	left outer join pubmed_pubs p on p.doi = f.doi
	left outer join scopus_pubs s on s.doi = f.doi
	order by f.doi, case when p.pm_id is null then s.pm_id else p.pm_id end, case when p.title is null then s.title else p.title end;
end; $function$
;
