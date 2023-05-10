import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.demo import *

title = "Profilo"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()
if user.has_access("investigator"):
    st.write("Utente: **" + user.name + "**")
    st.write("Età: **" + str(user.age) + "**")
    st.write("SCOPUS: **" + user.scopus_id + "**")
    st.write("Contratto: **" + user.contract + "**")
    st.write("Ultimo aggiornamento: **" + str(user.update_date) + "**")

    year = select_year(st)
    user.get_pubs(year)

