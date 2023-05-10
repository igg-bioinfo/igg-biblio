import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.demo import *
from classes.scopus import *
from classes.pubmed import *
from classes.scival import *

set_title(st)

db = DB(st)
db.connect()
user = User(st, db)
if user.login():

    year = select_year(st)

    st.markdown("#### Anagrafica")
    st.markdown("###### Ricercatori per l'anno: " + str(year) + "")
    demo = Demo(st, db, year)
    if demo.get_update_details():
        st.write("Ultimo aggiornamento: **" + str(demo.update_date) + " ("+ str(demo.update_days) + " giorni fa)**")
        st.write("Ricercatori: **" + str(demo.update_count) + "**")
    demo.upload_excel()

    def set_pubs_row(obj):
        if obj.get_update_details():
            st.write("Ultimo aggiornamento: **" + str(obj.update_date) + " ("+ str(obj.update_days) + " giorni fa)**")
            st.write("Pubblicazioni: **" + str(obj.update_count_pubs) + "**")
            st.write("Autori per tutte le pubblicazioni: **" + str(obj.update_count_authors) + "**")
        obj.import_pubs()


    st.markdown("---")
    st.markdown("#### Scopus")
    st.markdown("###### Pubblicazioni per l'anno: " + str(year) + "")
    scopus = Scopus(st, db, year)
    set_pubs_row(scopus)


    st.markdown("---")
    st.markdown("#### PubMed")
    st.markdown("###### Pubblicazioni per l'anno: " + str(year) + "")
    pubmed = Pubmed(st, db, True, year)
    set_pubs_row(pubmed)


    st.markdown("---")
    st.markdown("#### Albo")
    st.markdown("###### Ricercatori con H-Index per l'anno: " + str(year) + "")
    scival = Scival(st, db, year)
    if scival.get_update_details():
        st.write("Ultimo aggiornamento: **" + str(scival.update_date) + " ("+ str(scival.update_days) + " giorni fa)**")
        st.write("Ricercatori con H-Index: **" + str(scival.update_count) + "**")
    scival.import_metrics()

db.close()
#   conda activate streamlit
#   streamlit run 0_Home.py