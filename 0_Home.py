import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.demo import *
from classes.scopus import *
#from classes.pubmed import *

set_title(st)

db = DB(st)
db.connect()
user = User(st, db)
if user.login():

    year = select_year(st)

    st.markdown("#### Anagrafica " + str(year))
    demo = Demo(st, db, year)
    if demo.get_update_details():
        st.write("L'ultimo aggiornamento del **" + str(demo.update_date) + " ("+ str(demo.update_days) + " giorni fa)**")
        st.write("Teste totali: **" + str(demo.update_count) + "**")
        st.write("Teste con Scopus ID: **" + str(demo.update_count_filter) + "**") # con Scopus ID e ancora attivi
    demo.upload_excel()
    #st.markdown("###### Autori con affiliazione Gaslini recuperati da Scopus")
    #scopus_autori = Scopus(st, db, year)
    #if scopus_autori.get_authors_update_details():
    #    st.write("Ultimo aggiornamento: **" + str(scopus_autori.update_date) + " ("+ str(scopus_autori.update_days) + " giorni fa)**")
    #    st.write("Ricercatori da Scopus: **" + str(scopus_autori.update_count_authors) + "**")
    #scopus_autori.import_authors()

    def set_pubs_row(obj):
        if obj.get_update_details():
            st.write("Ultimo aggiornamento: **" + str(obj.update_date) + " ("+ str(obj.update_days) + " giorni fa)**")
            st.write("Pubblicazioni: **" + str(obj.update_count_pubs) + "**")
            st.write("Autori per tutte le pubblicazioni: **" + str(obj.update_count_authors) + "**")
        obj.import_pubs_by_year()

    st.markdown("---")
    st.markdown("#### Albo " + str(year))
    scopus_albo = Scopus(st, db, year)
    if scopus_albo.get_metrics_update_details():
        st.write("Ultimo aggiornamento: **" + str(scopus_albo.update_date) + " ("+ str(scopus_albo.update_days) + " giorni fa)**")
        for updates in scopus_albo.metrics_update:
            st.write("L'aggiornamento del **" + str(updates["update"]) + "** ha coinvolto pubblicazioni e metriche di **" + str(updates["metrics"]) + "** ricercatori.")
    scopus_albo.import_metrics()

    st.markdown("---")
    st.markdown("#### PUC da Scopus")
    scopus_pucs = Scopus(st, db, year)
    st.write("I primi nomi, gli ultimi nomi e i corresponding vengono recuperati interrogando Scopus pubblicazione per pubblicazione.")
    if scopus_pucs.get_pucs_update_details():
        bt_text = "Recupera i PUC mancanti per " + str(scopus_pucs.pucs_missing) + " pubblicazioni "
        bt_text += "(max. " + str(max_pucs) + " alla volta)"
        if st.button(bt_text, key="scopus_pucs"):
            scopus_pucs.import_pucs()

    st.markdown("---")
    st.markdown("#### Scopus - Pubblicazioni " + str(year))
    scopus = Scopus(st, db, year)
    set_pubs_row(scopus)


    #st.markdown("---")
    #st.markdown("#### PubMed - Pubblicazioni " + str(year))
    #pubmed = Pubmed(st, db, True, year)
    #set_pubs_row(pubmed)

db.close()



#   conda activate streamlit
#   streamlit run 0_Home.py
#   sudo systemctl start biblio.service
#   sudo systemctl stop biblio.service