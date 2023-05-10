import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.scopus import *

title = "Scopus"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

year = select_year(st)

scopus = Scopus(st, db, year)
scopus.get_failed_details()
if scopus.get_update_details():
    st.write("Ultimo aggiornamento: **" + str(scopus.update_date) + " ("+ str(scopus.update_days) + " giorni fa)**")
    st.write("Pubblicazioni: **" + str(scopus.update_count_pubs) + "**")
    st.write("Autori per tutte le pubblicazioni: **" + str(scopus.update_count_authors) + "**")
    scopus.get_pubs_authors_for_year()
else:
    st.error("Nessun dato presente")

db.close()