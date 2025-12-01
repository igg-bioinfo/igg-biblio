-- DROP FUNCTION public.pubs_matching_author(int4, varchar);

CREATE OR REPLACE FUNCTION public.pubs_matching_author(pub_year integer, author character varying)
 RETURNS TABLE(doi character varying, pm_id character varying, title character varying, pub_name character varying, scopus_name character varying, author_scopus character varying)
 LANGUAGE plpgsql
AS $function$
begin
    RETURN QUERY
	select distinct f.doi, 
	case when p.pm_id is null then s.pm_id else p.pm_id end as pm_id, 
	case when p.title is null then s.title else p.title end as title,
	p.author_name as pub_name, 
	s.author_name as scopus_name, 
	s.author_scopus
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
	where lower(s.author_name) like '%' || $2 || '%' or lower(p.author_name) like '%' || $2 || '%'
	order by f.doi, case when p.pm_id is null then s.pm_id else p.pm_id end, case when p.title is null then s.title else p.title end;
end; $function$
;
