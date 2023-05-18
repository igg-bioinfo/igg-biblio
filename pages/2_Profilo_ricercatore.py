import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.demo import *
from classes.scopus import *

title = "Profilo ricercatore"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()
is_admin = user.has_access("admin")
investigator = None
if is_admin:
    demo = Demo(st, db, datetime.now().year)
    invs = []
    for inv in demo.get_all_from_db():
        invs.append(inv[0])
    inv_name = st.multiselect('Ricercatore:', invs, max_selections= 1)
    if inv_name:
        investigator = User(st, db, inv_name[0])
else:
    investigator = user
    st.write("Utente: **" + investigator.name + "**")
    
if investigator:
    if investigator.update_date:
        st.write("Ultimo aggiornamento dell'anagrafica: **" + str(investigator.update_date) + "**")
    st.markdown("---")

    st.markdown("#### Dettagli")
    set_prop(st, "Età", investigator.age)
    set_prop(st, "Contratto", investigator.contract)
    scopus_id = st.text_input("SCOPUS ID:", value=investigator.scopus_id if investigator.scopus_id else "")
    orcid_id = st.text_input("ORCID ID:", value=investigator.orcid_id if investigator.orcid_id else "")
    investigator.save_ids(scopus_id, orcid_id)
    st.markdown("---")

    st.markdown("#### Metriche")
    year = datetime.now().year
    investigator.get_metrics(year)
    col_all, col_5years = st.columns([1,3])
    with col_all:
        st.write("**Totale**")
        set_prop(st, "H-index", investigator.hindex)
        set_prop(st, "Pubblicazioni", investigator.n_pubs)
        set_prop(st, "Citazioni", investigator.all_cited)
    with col_5years:
        st.write("**Ultimi 5 anni**")
        set_prop(st, "H-index", investigator.hindex5)
        set_prop(st, "Pubblicazioni", investigator.n_pubs5)
        set_prop(st, "Citazioni", investigator.all_cited5)
    if investigator.scopus_id:
        if st.button("Aggiorna pubblicazioni e metriche", key="scopus_details_all"):
            with st.spinner():
                scopus = Scopus(st, db, year)
                scopus.import_pubs(True, investigator.scopus_id)
                st.experimental_rerun()
    else:
        st.error("Scopus id non presente")
    st.markdown("---")

    st.markdown("#### Pubblicazioni")
    year_pubs = select_year(st, True)
    investigator.get_pubs(year_pubs)

db.close()

