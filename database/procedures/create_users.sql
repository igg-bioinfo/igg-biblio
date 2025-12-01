-- DROP PROCEDURE public.create_users();

CREATE OR REPLACE PROCEDURE public.create_users()
 LANGUAGE plpgsql
AS $procedure$
	DECLARE cur_invs CURSOR FOR
		select inv_name from investigators where scopus_id is not null and inv_name not in (select name from users) and update_year = date_part('year', CURRENT_DATE);
		v_name text;
		v_email text;
		a_email text[];
	BEGIN
		OPEN cur_invs;
		LOOP
  			FETCH cur_invs INTO v_name; 
      		EXIT WHEN NOT FOUND;
			raise notice '%', v_name;
      		select string_to_array(LOWER(v_name), ' ') into a_email;
      	
			if array_length(a_email, 1) > 2 then
				if array_length(a_email, 1) > 3 then
					v_email = a_email[2] || a_email[1];
				else
					v_email = a_email[3] || a_email[1] || a_email[2];
				end if;
			elseif array_length(a_email, 1) > 1 then
				v_email = a_email[2] || a_email[1];
			else
				v_email = a_email[1];
			end if;
			v_email = v_email || '@gaslini.org';
			insert into users (user_name, user_password, user_type, "name") 
			VALUES(v_email, LOWER(substr(concat(md5(random()::text), md5(random()::text)), 0, 8)), 'investigator', v_name);
			raise notice '%', v_email;
		END LOOP;
		CLOSE cur_invs;
	END;
$procedure$
;
