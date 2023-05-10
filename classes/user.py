import pandas as pd
from datetime import datetime 

class User:
    st = None
    db = None
    id = 0
    name = ""
    user_name = ""
    user_type = ""
    contract = ""
    scopus_id = ""
    age = ""
    update_date = ""


    def __init__(self, st, db):
        self.st = st
        self.db = db
        if "logged_user" in self.st.session_state and self.st.session_state["logged_user"] != None:
            user = self.st.session_state["logged_user"]
            self.id = user['id']
            self.name = user['name']
            self.user_name = user['user_name']
            self.user_type = user['user_type']
            if self.has_access("investigator"):
                self.get_investigator()
            self.set_logout()
    
    def get_investigator(self):
        self.db.cur.execute("SELECT scopus_id, contract, FLOOR((DATE_PART('day', now() - date_birth) / 365)::float) as age, update_date FROM investigators WHERE inv_name = %s and update_year = %s ",
                            [self.name, datetime.now().year])
        res = self.db.cur.fetchone()
        if res != None:
            self.scopus_id = res[0] 
            self.contract = res[1] 
            self.age = int(res[2])
            self.update_date = res[3] 
    
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

    def get_pubs(self, year):
        with self.st.spinner():
            if self.scopus_id != None and self.scopus_id != "":
                self.db.cur.execute("select doi, pm_id, title, pub_date from scopus_pubs where author_scopus = %s and update_year = %s ",
                                [self.scopus_id, year])
                res = self.db.cur.fetchall()
                df = pd.DataFrame(res, columns=["DOI", "PUBMED", "Titolo", "Data"])
                self.st.dataframe(df, height=666)
            

        