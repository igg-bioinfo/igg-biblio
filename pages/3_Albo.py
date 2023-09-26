import streamlit as st
from utils import *
from classes.db_psql import *
from classes.user import *
from classes.demo import *
from classes.scopus import *
#from classes.scival import *

title = "Albo"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()


year = select_year(st)
scopus = Scopus(st, db, year)
if scopus.get_metrics_update_details():
    st.write("Ultimo aggiornamento: **" + str(scopus.update_date) + " ("+ str(scopus.update_days) + " giorni fa)**")
    for updates in scopus.metrics_update:
        st.write("L'aggiornamento del **" + str(updates["update"]) + "** ha coinvolto pubblicazioni e metriche di **" + str(updates["metrics"]) + "** ricercatori.")
    scopus.get_albo()
else:
    st.error("Nessun dato presente")

db.close()