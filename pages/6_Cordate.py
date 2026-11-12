import streamlit as st
from utils import *
from classes.db_psql import *
from classes.user import *
from classes.demo import *
from classes.statistics import *
from classes.cohort import *

title = "Gestione delle cordate"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

year = datetime.now().year
demo = Demo(st, db, year)
cohort = Cohort(st, db)
stats = Statistics(st, db, year)

invs = []
for inv in demo.get_all_from_db():
    invs.append(inv[0])
max_cohort = 50
if st.session_state.pop("clear_cohort_new", False):
    st.session_state["cohort_new"] = []
cohort_invs = []
if ("cohorts" not in st.session_state or len(st.session_state["cohorts"]) == 0):
    cohort_invs = st.multiselect('Scegli un massimo di ' + str(max_cohort) + ' ricercatori tra i ' + str(len(invs)) + ' presenti per l\'anno corrente:', invs, max_selections= max_cohort, key="cohort_new")
if ("cohorts" not in st.session_state or len(st.session_state["cohorts"]) == 0) and len(cohort_invs) > 0:
    stats.get_invs_by_names(cohort_invs)
    cohort.create(stats.inv_ids)
else:
    if ("cohorts" not in st.session_state or len(st.session_state["cohorts"]) == 0):
        st.write("Oppure")
    cohorts = cohort.get_all()
    if st.session_state.pop("clear_cohorts", False):
        st.session_state["cohorts"] = []
    cohort_row = st.multiselect('Scegli una cordata gia creata:', cohorts, max_selections= 1, key="cohorts")
    if len(cohort_row) > 0:
        cohort_name = cohort_row[0]
        inv_names = cohort.get_ids_by_name(cohort_name)
        cohort_invs = st.multiselect('Scegli un massimo di ' + str(max_cohort) + ' ricercatori tra i ' + str(len(invs)) + ' presenti per l\'anno corrente:', 
                                     invs, max_selections= max_cohort, default=inv_names, key="cohort_update")
        if len(cohort_invs) > 0:
            stats.get_invs_by_names(cohort_invs)
            cohort.update(cohort_name, stats.inv_ids)

    
db.close()
