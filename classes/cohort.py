import pandas as pd
from datetime import datetime 
from utils import *
from classes.user import *
from classes.doc2res import *

class Cohort:
    st = None
    db = None
    inv_ids = []


    def __init__(self, st, db):
        self.st = st
        self.db = db


    def create(self, inv_ids = []):
        self.inv_ids = inv_ids

        col1, col2 = self.st.columns([1, 5], vertical_alignment="bottom")
        with col1:
            cohort_name = self.st.text_input("Nome nuova cordata", key="cohort")
        with col2:
            btn_create = self.st.button("Salva cordata")
        if cohort_name.strip() and btn_create:
            with self.st.spinner("Creazione della cordata..."):
                sql = "INSERT INTO cohorts (name, ids) VALUES (%s, %s)"
                params = [cohort_name, ",".join(inv_ids)]
                self.db.cur.execute(sql, params)
                self.db.conn.commit()

                del self.st.session_state["cohort_new"]
                self.st.session_state["clear_cohort_new"] = True
                self.st.rerun()


    def update(self, cohort_name, inv_ids):
        self.inv_ids = inv_ids

        col1, col2 = self.st.columns([1, 5], vertical_alignment="bottom")
        with col1:
            btn_update = self.st.button("Aggiorna cordata")
        with col2:
            self.delete(cohort_name)
        if btn_update:
            with self.st.spinner("Aggiornamento della cordata..."):
                sql = "UPDATE cohorts SET ids = %s WHERE name = %s"
                params = [",".join(inv_ids), cohort_name]
                self.db.cur.execute(sql, params)
                self.db.conn.commit()

                del self.st.session_state["cohort_update"]
                self.st.session_state["clear_cohort_update"] = True
                del self.st.session_state["cohorts"]
                self.st.session_state["clear_cohorts"] = True
                self.st.rerun()


    def delete(self, cohort_name):
        if self.st.button("Elimina cordata"):
            with self.st.spinner("Eliminazione della cordata..."):
                sql = "DELETE FROM cohorts WHERE name = %s"
                params = [cohort_name]
                self.db.cur.execute(sql, params)
                self.db.conn.commit()

                del self.st.session_state["cohorts"]
                self.st.session_state["clear_cohorts"] = True
                self.st.rerun()



    def get_all(self):
        sql = "SELECT name FROM cohorts "
        self.db.cur.execute(sql)
        res = self.db.cur.fetchall()
        return [r[0] for r in res]


    def get_ids_by_name(self, name):
        sql = """SELECT ids FROM cohorts WHERE name = %s """
        self.db.cur.execute(sql, [name])
        res = self.db.cur.fetchone()
        inv_ids = str(res[0]).split(',') if len(res) > 0 else []
        inv_names = []
        for id in inv_ids:
            inv = User(self.st, self.db, id=id)
            inv_names.append(inv.name)
        return inv_names
