import pandas as pd
from datetime import datetime 
from utils import *

class User:
    st = None
    db = None
    id = 0
    name = ""
    user_name = ""
    user_type = ""
    contract = ""
    scopus_id = ""
    orcid_id = ""
    age = ""
    update_date = ""
    hindex = None
    n_pubs = None
    all_cited = None
    hindex5 = None
    n_pubs5 = None
    all_cited5 = None
    pucs_missing = None
    pucs = None
    pucs5 = None


    #-----------------------------------GENERALI
    def __init__(self, st, db, name = ""):
        self.st = st
        self.db = db
        if name != "":
            self.name = name
            self.get_investigator()
        elif "logged_user" in self.st.session_state and self.st.session_state["logged_user"] != None:
            user = self.st.session_state["logged_user"]
            self.id = user['id']
            self.name = user['name']
            self.user_name = user['user_name']
            self.user_type = user['user_type']
            if self.has_access("investigator"):
                self.get_investigator()
            self.set_logout()
    
    
    def get_investigator(self):
        sql = ""
        sql += "SELECT CASE WHEN d.scopus_id IS NULL THEN i.scopus_id ELSE d.scopus_id END as scopus_id, i.contract, " + age_field + " as age, "
        sql += "CASE WHEN d.orcid_id IS NULL THEN '' ELSE d.orcid_id END as orcid_id, "
        sql += "CASE WHEN d.update_date IS NULL THEN i.update_date ELSE d.update_date END as update_date "
        sql += "FROM investigators i "
        sql += "LEFT OUTER JOIN investigator_details d ON d.inv_name = i.inv_name "
        sql += "WHERE i.inv_name = %s and update_year = %s "
        self.db.cur.execute(sql, [self.name, datetime.now().year])
        res = self.db.cur.fetchone()
        if res != None:
            self.scopus_id = res[0] 
            self.contract = res[1] 
            self.age = int(res[2])
            self.orcid_id = res[3] 
            self.update_date = res[4] 


    def login(self):
        def check_get_user():
            self.db.cur.execute("SELECT user_id, user_name, user_type, name FROM users WHERE user_name = %s and user_password = %s",
                                [self.st.session_state["username"], self.st.session_state["password"]])
            res = self.db.cur.fetchone()
            if res != None:
                del self.st.session_state["username"]
                del self.st.session_state["password"]
                self.st.session_state["logged_user"] = {'id': res[0], 'name': res[3], 'user_name': res[1], 'user_type': res[2]}
                self.st.experimental_rerun()
            else:
                self.st.error("Credenziali errate")
                self.st.session_state["logged_user"] = None

        if "logged_user" not in self.st.session_state or self.st.session_state["logged_user"] == None:
            with self.st.form("login_form"):
                self.st.write("LOGIN")
                self.st.text_input("Utente", key="username")
                self.st.text_input("Password", type="password", key="password")
                if self.st.form_submit_button("Entra"):
                    with self.st.spinner():
                        check_get_user()
        else:
            return True
        return False


    def set_logout(self):
        with self.st.sidebar:
            self.st.markdown("Profilo: **" + self.name + "**")
            if self.st.button("Logout"):
                self.st.session_state["logged_user"] = None
                self.st.experimental_rerun()


    def is_logged(self):
        if "logged_user" not in self.st.session_state or self.st.session_state["logged_user"] == None:
            self.st.error("Accesso negato")
            self.st.stop()


    def has_access(self, type):
        has_access = False
        if type in self.user_type:
            has_access = True 
        return has_access


    #-----------------------------------AGGIORNA IDS
    def save_ids(self, scopus_id, orcid_id):   
        if self.st.button("Aggiorna gli IDs", key="save_ids"):
            with self.st.spinner():
                update_date = datetime.date(datetime.now())
                sql = "UPDATE investigator_details SET scopus_id=%s, orcid_id=%s, update_date=%s WHERE inv_name=%s "
                self.db.cur.execute(sql, [scopus_id, orcid_id, update_date, self.name])
                sql = "INSERT INTO investigator_details (inv_name, scopus_id, orcid_id, update_date) "
                sql += "SELECT %s, %s, %s, %s "
                sql += "WHERE NOT EXISTS (SELECT 1 FROM investigator_details WHERE inv_name = %s)"
                self.db.cur.execute(sql, [self.name, scopus_id, orcid_id, update_date, self.name])
                self.db.conn.commit()


    #-----------------------------------METRICHE BASE
    def get_metrics(self, year):
        with self.st.spinner():
            if self.scopus_id != None and self.scopus_id != "":
                sql = "select hindex, pubs, allcited, hindex5, pubs5, allcited5 from "
                if year == all_years:
                    year = datetime.now().year
                self.db.cur.execute(sql + "scopus_metrics where author_scopus = %s and update_year = %s ", [self.scopus_id, year])
                res = self.db.cur.fetchall()
                if res:
                    self.hindex = res[0][0]
                    self.n_pubs = res[0][1]
                    self.all_cited = res[0][2]
                    self.hindex5 = res[0][3]
                    self.n_pubs5 = res[0][4]
                    self.all_cited5 = res[0][5]


    def get_pubs(self, year):
        with self.st.spinner():
            if self.scopus_id != None and self.scopus_id != "":
                params = [self.scopus_id, self.scopus_id, self.scopus_id, 
                          self.scopus_id, self.scopus_id, self.scopus_id, 
                          self.scopus_id, self.scopus_id, self.scopus_id, self.scopus_id, self.scopus_id,
                          self.scopus_id]
                sql = "select s.eid, s.doi, s.pm_id, s.title, s.pub_date, s.cited, "
                sql += "CASE WHEN p.first1 = %s or p.first2 = %s or p.first3 = %s THEN 'Si' ELSE 'No' END as Primo, "
                sql += "CASE WHEN p.last1 = %s or p.last2 = %s or p.last3 = %s THEN 'Si' ELSE 'No' END as Ultimo, "
                sql += "CASE WHEN p.corr1 = %s or p.corr2 = %s or p.corr3 = %s or p.corr4 = %s or p.corr5 = %s THEN 'Si' ELSE 'No' END as Corr "
                sql += "FROM scopus_pubs" + ("_all" if year == all_years else "") + " s "
                sql += "LEFT OUTER JOIN scopus_pucs p ON p.eid = s.eid "
                sql += "WHERE author_scopus = %s "
                if year != all_years:
                    sql += "and update_year = %s "
                    params.append(year)
                sql += "ORDER BY pub_date DESC"
                self.db.cur.execute(sql, params)
                res = self.db.cur.fetchall()
                df = pd.DataFrame(res, columns=["EID", "DOI", "PUBMED ID", "Titolo pubblicazione", "Data", "Cit.", "Primo", "Ultimo", "Corr."])
                df.set_index('EID', inplace=True)
                download_excel(self.st, df, "scopus_pubs_" + self.scopus_id + "_" + str(year) + "_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
                self.st.write(str(len(df)) + " Righe")
                self.st.dataframe(df, height=row_height)


    #-----------------------------------PUC
    def check_pucs(self, year):
        params = [year, self.scopus_id]
        sql = "SELECT COUNT(eid) AS eids FROM scopus_pubs_all "
        sql += "WHERE update_year = %s and author_scopus = %s "
        sql += "and eid NOT IN (SELECT DISTINCT eid FROM scopus_pucs) GROUP BY author_scopus "
        self.db.cur.execute(sql, params)
        res = self.db.cur.fetchall()
        if res and len(res) > 0: 
            if len(res[0]) > 0:
                self.pucs_missing = res[0][0]
                if self.pucs_missing == None or self.pucs_missing == 0:   
                    return True
                elif self.pucs_missing == self.n_pubs:
                    self.st.error("Mancano i PUC di tutte le pubblicazioni per stimare i PUC per l'autore")
                    return False
                else:
                    self.st.error("Mancano i PUC per " + str(self.pucs_missing) + " pubblicazioni per stimare i PUC per l'intera carriera")
                    return False
            else:
                self.st.error("Mancano i PUC di tutte le pubblicazioni per stimare i PUC per l'autore")
                return False
        else: 
            return True
    
    
    def get_condition(self, year, pub_year, is_all):
        last_5years = year - 5
        return (pub_year <= year) if is_all else (pub_year <= year and pub_year >= last_5years)
    

    def get_pucs(self, year):
        self.pucs = ""
        self.pucs5 = ""
        sql = ""
        sql += "SELECT l.*, COUNT(c.eid) as corrs FROM ( "
        sql += "SELECT f.*, COUNT(l.eid) as lasts FROM ( "
        sql += "SELECT s.*, COUNT(f.eid) as firsts FROM ( "
        sql += "SELECT DISTINCT author_scopus AS scopus, EXTRACT('Year' from TO_DATE(pub_date,'YYYY-MM-DD')) as pub_year "
        sql += "FROM scopus_pubs_all WHERE author_scopus = %s "
        sql += ") s "
        sql += "left outer join scopus_pucs f on s.pub_year = f.pub_year and (s.scopus = f.first1 or s.scopus = f.first2 or s.scopus = f.first3)"
        sql += "GROUP BY s.scopus, s.pub_year"
        sql += ") f "
        sql += "left outer join scopus_pucs l on f.pub_year = l.pub_year and (f.scopus = l.last1 or f.scopus = l.last2 or f.scopus = l.last3)"
        sql += "GROUP BY f.scopus, f.pub_year, firsts "
        sql += ") l "
        sql += "left outer join scopus_pucs c on l.pub_year = c.pub_year and (l.scopus = c.corr1 or l.scopus = c.corr2 or l.scopus = c.corr3 or l.scopus = c.corr4 or l.scopus = c.corr5)"
        sql += "GROUP BY l.scopus, l.pub_year, firsts, lasts "
        params = [self.scopus_id]
        self.db.cur.execute(sql, params)
        res = self.db.cur.fetchall()

        firsts = 0
        lasts = 0
        corrs = 0
        firsts5 = 0
        lasts5 = 0
        corrs5 = 0
        for r in res:
            if self.get_condition(year, r[1], True):
                firsts += int(r[2])
                lasts += int(r[3])
                corrs += int(r[4])
            if self.get_condition(year, r[1], False):
                firsts5 += int(r[2])
                lasts5 += int(r[3])
                corrs5 += int(r[4])
        self.pucs = str(firsts) + " - " + str(lasts) + " - " + str(corrs)
        self.pucs5 = str(firsts5) + " - " + str(lasts5) + " - " + str(corrs5)


        