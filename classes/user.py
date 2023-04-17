
class User:
    st = None
    db = None
    id = 0
    name = ""
    user_name = ""
    user_type = ""


    def __init__(self, st, db):
        self.st = st
        self.db = db
        if "logged_user" in self.st.session_state and self.st.session_state["logged_user"] != None:
            user = self.st.session_state["logged_user"]
            print(user)
            self.id = user['id']
            self.name = user['name']
            self.user_name = user['user_name']
            self.user_type = user['user_type']
            self.set_logout()
    
    def login(self):
        def check_get_user():
            self.db.cur.execute('SELECT user_id, user_name, user_type, name FROM users WHERE user_name = %s and user_password = %s',
                                (self.st.session_state["username"], self.st.session_state["password"]))
            res = self.db.cur.fetchone()
            if res != None:
                self.st.session_state["logged_user"] = {'id': res[0], 'name': res[3], 'user_name': res[1], 'user_type': res[2]}
                print(self.st.session_state["logged_user"])
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

        