-- public.view_invs source

CREATE OR REPLACE VIEW public.view_invs
AS SELECT floor(date_part('day'::text, now() - i.date_birth::timestamp with time zone) / 365::double precision) AS age,
    i.inv_name,
        CASE
            WHEN d.first_name IS NULL OR d.first_name::text = ''::text THEN i.first_name
            ELSE d.first_name
        END AS first_name,
        CASE
            WHEN d.last_name IS NULL OR d.last_name::text = ''::text THEN i.last_name
            ELSE d.last_name
        END AS last_name,
        CASE
            WHEN u.user_name IS NULL OR u.user_name::text = ''::text THEN i.email
            ELSE u.user_name
        END AS user_name,
        CASE
            WHEN d.unit IS NULL OR d.unit::text = ''::text THEN i.unit
            ELSE d.unit
        END AS unit,
        CASE
            WHEN d.contract IS NULL OR d.contract::text = ''::text THEN i.contract
            ELSE d.contract
        END AS contract,
        CASE
            WHEN d.scopus_id IS NULL OR d.scopus_id::text = ''::text THEN i.scopus_id
            ELSE d.scopus_id
        END AS scopus_id,
        CASE
            WHEN d.orcid_id IS NULL OR d.orcid_id::text = ''::text THEN i.orcid_id
            ELSE d.orcid_id
        END AS orcid_id,
        CASE
            WHEN d.researcher_id IS NULL OR d.researcher_id::text = ''::text THEN i.researcher_id
            ELSE d.researcher_id
        END AS researcher_id,
        CASE
            WHEN d.inv_name IS NULL THEN '0'::text
            ELSE '1'::text
        END AS user_confirmed,
        CASE
            WHEN d.update_date IS NULL OR d.update_date::text = ''::text THEN i.update_date
            ELSE d.update_date
        END AS update_date,
    i.update_year,
    i.date_birth,
    i.email2,
    i.is_workflow,
    i.date_end
   FROM investigators i
     LEFT JOIN investigator_details d ON d.inv_name::text = i.inv_name::text
     LEFT JOIN users u ON u.name::text = i.inv_name::text;