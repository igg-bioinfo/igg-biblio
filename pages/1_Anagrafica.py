import streamlit as st
from utils import *
from classes.db_psql import *
from classes.user import *
from classes.demo import *

title = "Anagrafica"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

year = select_year(st, db)

demo = Demo(st, db, year)
if demo.get_update_details():
    st.write("L'ultimo aggiornamento è del **" + str(demo.update_date) + " ("+ str(demo.update_days) + " giorni fa)**")
    st.write("Teste con Scopus ID: **" + str(demo.update_count_filter) + "**") # con Scopus ID e ancora attivi
    demo.get_all()
else:
    st.error("Nessun dato presente")

db.close()

