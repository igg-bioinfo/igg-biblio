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
    is_admin = user.has_access("admin")

    year = select_year(st)

    st.markdown("#### Anagrafica " + str(year))
    demo = Demo(st, db, year)
    if demo.get_update_details():
        st.write("Ultimo aggiornamento: **" + str(demo.update_date) + " ("+ str(demo.update_days) + " giorni fa)**")
        st.write("Ricercatori: **" + str(demo.update_count) + "**")
    if is_admin:
        demo.upload_excel()

    def set_pubs_row(obj):
        if obj.get_update_details():
            st.write("Ultimo aggiornamento: **" + str(obj.update_date) + " ("+ str(obj.update_days) + " giorni fa)**")
            st.write("Pubblicazioni: **" + str(obj.update_count_pubs) + "**")
            st.write("Autori per tutte le pubblicazioni: **" + str(obj.update_count_authors) + "**")
        if is_admin:
            obj.import_pubs_by_year()

    st.markdown("---")
    st.markdown("#### Albo " + str(year))
    scopus_albo = Scopus(st, db, year)
    if scopus_albo.get_metrics_update_details():
        st.write("Ultimo aggiornamento: **" + str(scopus_albo.update_date) + " ("+ str(scopus_albo.update_days) + " giorni fa)**")
        st.write("Ricercatori con SCOPUS ID: **" + str(scopus_albo.update_count) + "**")
        if is_admin:
            scopus_albo.import_metrics()


    st.markdown("---")
    st.markdown("#### Scopus - Pubblicazioni " + str(year))
    scopus = Scopus(st, db, year)
    set_pubs_row(scopus)


    st.markdown("---")
    st.markdown("#### PubMed - Pubblicazioni " + str(year))
    pubmed = Pubmed(st, db, True, year)
    set_pubs_row(pubmed)

db.close()
#   conda activate streamlit
#   streamlit run 0_Home.py