import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.demo import *
from classes.scival import *

import requests
import json
proxies = {
    'http': 'http://fg-proxy-c.gaslini.lan:8080',
    'https': 'http://fg-proxy-c.gaslini.lan:8080',
}

title = "Albo"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

year = select_year(st)

scival = Scival(st, db, year)
if scival.get_update_details():
    st.write("Ultimo aggiornamento: **" + str(scival.update_date) + " ("+ str(scival.update_days) + " giorni fa)**")
    st.write("H-Indexes: **" + str(scival.update_count) + "**")
    scival.get_albo()
else:
    st.error("Nessun dato presente")

db.close()