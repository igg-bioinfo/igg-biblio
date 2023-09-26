import streamlit as st
from utils import *
from classes.db_psql import *
from classes.user import *
from classes.scopus import *
from classes.pubmed import *

title = "Pubblicazioni di Scopus per anno"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

year = select_year(st, db, 'scopus_pubs_all')

scopus = Scopus(st, db, year)
scopus.get_failed_details("by_year")
if scopus.get_update_details():
    st.write("Ultimo aggiornamento: **" + str(scopus.update_date) + " ("+ str(scopus.update_days) + " giorni fa)**")
    #st.write("Pubblicazioni: **" + str(scopus.update_count_pubs) + "**")
    st.write("Autori per tutte le pubblicazioni: **" + str(scopus.update_count_authors) + "**")
    scopus.get_pubs_authors_for_year()

    if year != all_years:
        st.markdown("---")

        st.markdown("#### Pubblicazioni di Pubmed")
        st.write("Pubblicazioni di Pubmed non presenti nella banca dati Scopus")
        pubmed = Pubmed(st, db, True, year)
        if pubmed.get_update_details():
            st.write("Ultimo aggiornamento: **" + str(pubmed.update_date) + " ("+ str(pubmed.update_days) + " giorni fa)**")
            #st.write("Pubblicazioni: **" + str(pubmed.update_count_pubs) + "**")
            #st.write("Autori per tutte le pubblicazioni: **" + str(pubmed.update_count_authors) + "**")
            pubmed.get_no_scopus_pubs_authors_for_year()
        else:
            st.error("Nessun dato presente")
else:
    st.error("Nessun dato presente")

db.close()