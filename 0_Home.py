import streamlit as st
from functions.utils import *
from classes.db_psql import *
from classes.user import *
from classes.demo import *

set_title(st)

db = DB(st)
db.connect()
user = User(st, db)
if user.login():

    st.markdown("#### Anagrafica:")
    demo = Demo(st, db)
    if demo.get_update_details():
        st.write("Ultimo aggiornamento il **" + str(demo.update_date) + " ("+ str(demo.update_days) + " giorni fa)** e sono presenti **" + str(demo.update_count) + "** ricercatori")
        if demo.update_days > 3 and st.button("Importa excel file"):
            with st.spinner():
                st.write("Aggiorna")
    else:
        st.write("Nessun aggiornamento")

db.close()
#   streamlit run 0_Home.py