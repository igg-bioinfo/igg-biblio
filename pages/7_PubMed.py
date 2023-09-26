import streamlit as st
from utils import *
from classes.db_psql import *
from classes.user import *
from classes.pubmed import *

title = "Pubblicazioni di PubMed per anno"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

year = select_year(st, db, 'pubmed_pubs')

pubmed = Pubmed(st, db, True, year)
if pubmed.get_update_details():
    st.write("Ultimo aggiornamento: **" + str(pubmed.update_date) + " ("+ str(pubmed.update_days) + " giorni fa)**")
    #st.write("Pubblicazioni: **" + str(pubmed.update_count_pubs) + "**")
    st.write("Autori per tutte le pubblicazioni: **" + str(pubmed.update_count_authors) + "**")
    pubmed.get_pubs_authors_for_year()
else:
    st.error("Nessun dato presente")

db.close()