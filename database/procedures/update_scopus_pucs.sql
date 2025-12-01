-- DROP PROCEDURE public.update_scopus_pucs(varchar, varchar);

CREATE OR REPLACE PROCEDURE public.update_scopus_pucs(scopus_old character varying, scopus_new character varying)
 LANGUAGE plpgsql
AS $procedure$
begin
update scopus_pucs set first1 = scopus_new where first1 = scopus_old;
update scopus_pucs set first2 = scopus_new where first2 = scopus_old;
update scopus_pucs set first3 = scopus_new where first3 = scopus_old;

update scopus_pucs set last1 = scopus_new where last1 = scopus_old;
update scopus_pucs set last2 = scopus_new where last2 = scopus_old;
update scopus_pucs set last3 = scopus_new where last3 = scopus_old;

update scopus_pucs set corr1 = scopus_new where corr1 = scopus_old;
update scopus_pucs set corr2 = scopus_new where corr2 = scopus_old;
update scopus_pucs set corr3 = scopus_new where corr3 = scopus_old;
update scopus_pucs set corr4 = scopus_new where corr4 = scopus_old;
update scopus_pucs set corr5 = scopus_new where corr5 = scopus_old;
end;
$procedure$
;
