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

    def get_pubs(self, year):
        with self.st.spinner():
            if self.scopus_id != None and self.scopus_id != "":
                sql = "select doi, pm_id, title, pub_date, cited from "
                if year == all_years:
                    self.db.cur.execute(sql + "scopus_pubs_all where author_scopus = %s ORDER BY pub_date DESC",
                                    [self.scopus_id])
                else:
                    self.db.cur.execute(sql + "scopus_pubs where author_scopus = %s and update_year = %s ORDER BY pub_date DESC",
                                    [self.scopus_id, year])
                res = self.db.cur.fetchall()
                df = pd.DataFrame(res, columns=["DOI", "PUBMED ID", "Titolo pubblicazione", "Data", "Citazioni "])
                df.set_index('DOI', inplace=True)
                download_excel(self.st, df, "scopus_pubs_" + self.scopus_id + "_" + str(year) + "_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
                self.st.write(str(len(df)) + " Righe")
                self.st.dataframe(df, height=row_height)
            

        