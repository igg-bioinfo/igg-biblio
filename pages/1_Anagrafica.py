import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.demo import *

title = "Anagrafica"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()
admin_access(st, user)

year = select_year(st)

demo = Demo(st, db, year)
if demo.get_update_details():
    st.write("Ultimo aggiornamento: **" + str(demo.update_date) + " ("+ str(demo.update_days) + " giorni fa)**")
    st.write("Ricercatori: **" + str(demo.update_count) + "**")
    demo.get_all()
else:
    st.error("Nessun dato presente")

db.close()

