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
investigator = None
demo = Demo(st, db, datetime.now().year)
invs = []
for inv in demo.get_all_from_db():
    invs.append(inv[0])
inv_name = st.multiselect('Ricercatore:', invs, max_selections= 1)
if inv_name:
    investigator = User(st, db, inv_name[0])
    
if investigator:
    if investigator.update_date:
        st.write("Ultimo aggiornamento dell'anagrafica: **" + str(investigator.update_date) + "**")
    st.markdown("---")

    st.markdown("#### Dati del ricercatore")
    user_name = st.text_input("Email Gaslini / username:", value=investigator.user_name if investigator.user_name else "")
    first_name = st.text_input("Nome:", value=investigator.first_name if investigator.first_name else "")
    last_name = st.text_input("Cognome:", value=investigator.last_name if investigator.last_name else "")
    if first_name == "" or last_name == "":
        st.error("Compila il tuo nome e cognome correttamente")
    set_prop(st, "Età", investigator.age)
    contract = st.text_input("Contratto:", value=investigator.contract if investigator.contract else "")
    unit = st.text_input("Unità operativa:", value=investigator.unit if investigator.unit else "")
    scopus_id = st.text_input("SCOPUS ID:", value=investigator.scopus_id if investigator.scopus_id else "")

    orcid_id = st.text_input("ORCID ID:", value=investigator.orcid_id if investigator.orcid_id else "")
    researcher_id = st.text_input("Researcher ID:", value=investigator.researcher_id if investigator.researcher_id else "")
    investigator.save_ids(first_name, last_name, user_name, contract, scopus_id, orcid_id, researcher_id)
    st.markdown("---")

    if investigator.first_name != "" or investigator.last_name != "":
        st.markdown("**Controlla su Scopus di non avere identificativi doppi a tuo nome al seguente link:**")
        html = ""
        html += "<a href='https://www.scopus.com/results/authorNamesList.uri?name=name&st1="
        names = first_name.split(" ")
        name_initials = []
        for n in names:
            name_initials.append(n[0])
        html += last_name.replace(" ", "+") + "&st2=" + "+".join(name_initials) + "&origin=searchauthorlookup'>"
        html += "Link a Scopus</a>"
        st.markdown(html, unsafe_allow_html=True)
        st.markdown("**In caso di identificativi multipli:**")
        st.markdown("* Loggati a Scopus con le tue credenziali")
        st.markdown("* Seleziona gli identificativi multipli")
        st.markdown("* Clicca sull'opzione 'Request to merge authors'")
        st.markdown("* Segui le istruzioni della banca dati")
    st.markdown("---")

    st.markdown("#### Metriche da Scopus")
    year_current = datetime.now().year
    investigator.get_metrics(year_current)
    st.write("Ultimo aggiornamento: **" + str(investigator.metrics_date) + "**")
    has_all_pucs = investigator.check_pucs(year_current)
    if has_all_pucs:
        investigator.get_pucs(year_current)
    col_5years, col_10years, col_all = st.columns([1,1,1])
    with col_5years:
        st.write("**Ultimi 5 anni**")
        set_prop(st, "H-index", investigator.hindex5)
        set_prop(st, "Pubblicazioni", investigator.n_pubs5)
        set_prop(st, "Citazioni", investigator.all_cited5)
        set_prop(st, "PUC", investigator.pucs5 if has_all_pucs else None)
    with col_10years:
        st.write("**Ultimi 10 anni**")
        set_prop(st, "H-index", investigator.hindex10)
        set_prop(st, "Pubblicazioni", investigator.n_pubs10)
        set_prop(st, "Citazioni", investigator.all_cited10)
        set_prop(st, "PUC", investigator.pucs10 if has_all_pucs else None)
    with col_all:
        st.write("**Totale**")
        set_prop(st, "H-index", investigator.hindex)
        set_prop(st, "Pubblicazioni", investigator.n_pubs)
        set_prop(st, "Citazioni", investigator.all_cited)
        set_prop(st, "PUC", investigator.pucs if has_all_pucs else None)

    if investigator.scopus_id:
        scopus = Scopus(st, db, year_current)
        if st.button("Aggiorna pubblicazioni e metriche", key="scopus_details_all"):
            with st.spinner():
                scopus.import_pubs(True, investigator.scopus_id)
                st.experimental_rerun()
        if investigator.n_pubs and investigator.n_pubs > 0:
            if has_all_pucs == False:
                bt_text = "Recupera i PUC mancanti per " + str(investigator.pucs_missing) + " pubblicazioni "
                bt_text += "(max. " + str(scopus.max_pucs) + " alla volta)"
                if st.button(bt_text, key="scopus_pucs"):
                    scopus.import_pucs(investigator.scopus_id)
    else:
        st.error("Scopus id non presente")
    st.markdown("---")

    st.markdown("#### Pubblicazioni di Scopus")
    st.write("Pubblicazioni ricavate unicamente dalla banca dati Scopus")
    year_pubs = select_year(st, True)
    investigator.get_pubs(year_pubs)

db.close()

