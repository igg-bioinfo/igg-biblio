import streamlit as st
from utils import set_title
from classes.db_psql import *
from classes.user import *
from classes.demo import *
from classes.pubmed import *

set_title(st)
days_demo = 3
days_pubmed = 7

db = DB(st)
db.connect()
user = User(st, db)
if user.login():

    st.markdown("#### Anagrafica ricercatori")
    demo = Demo(st, db)
    if demo.get_update_details():
        st.write("Ultimo aggiornamento: **" + str(demo.update_date) + " ("+ str(demo.update_days) + " giorni fa)**")
        st.write("Ricercatori: **" + str(demo.update_count) + "**")
    else:
        st.error("Nessun dato presente")
    if demo.update_date == None or demo.update_days >= days_demo:
        demo.upload_excel()
    else:
        st.warning("E' possibile aggiornare i dati passati " + str(days_demo) + " giorni")


    st.markdown("#### PubMed")
    st.markdown("###### Pubblicazioni dell'anno in corso:")
    pubmed = Pubmed(st, db)
    if pubmed.get_update_details():
        st.write("Ultimo aggiornamento: **" + str(pubmed.update_date) + " ("+ str(pubmed.update_days) + " giorni fa)**")
        st.write("Pubblicazioni: **" + str(pubmed.update_count_pubs) + "**")
        st.write("Autori per tutte le pubblicazioni: **" + str(pubmed.update_count_authors) + "**")
    else:
        st.error("Nessun dato presente")
    if pubmed.update_date == None or pubmed.update_days >= days_pubmed:
        pubmed.import_pubs()
    else:
        st.warning("E' possibile aggiornare i dati passati " + str(days_pubmed) + " giorni")

    year_prev = datetime.now().year - 1
    st.markdown("###### Pubblicazioni del " + str(year_prev) + ":")
    pubmed = Pubmed(st, db, year_prev)
    if pubmed.get_update_details():
        st.write("Ultimo aggiornamento: **" + str(pubmed.update_date) + " ("+ str(pubmed.update_days) + " giorni fa)**")
        st.write("Pubblicazioni: **" + str(pubmed.update_count_pubs) + "**")
        st.write("Autori per tutte le pubblicazioni: **" + str(pubmed.update_count_authors) + "**")
    else:
        st.error("Nessun dato presente")
    if pubmed.update_date == None or pubmed.update_days >= days_pubmed:
        pubmed.import_pubs()
    else:
        st.warning("E' possibile aggiornare i dati passati " + str(days_pubmed) + " giorni")

db.close()
#   streamlit run 0_Home.py