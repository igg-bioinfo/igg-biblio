import streamlit as st
from functions.utils import *
from classes.db_psql import *
from classes.user import *

set_title(st)

db = DB(st)
db.connect()
user = User(st, db)
if user.login():
    import pandas as pd
    from datetime import datetime 

    db.cur.execute('SELECT date_update, count(inv_id) FROM investigators  WHERE date_update = (SELECT MAX(date_update) FROM investigators) GROUP BY date_update')
    res = db.cur.fetchall()
    df = pd.DataFrame(res, columns=["update", "id"])
    date = df["update"][0]
    count = df["id"][0]
    dt = datetime.date(datetime.now()) - date

    st.markdown("#### Anagrafica:")
    st.write("Ultimo aggiornamento il **" + str(date) + " ("+ str(dt.days) + " giorni fa)** e sono presenti **" + str(count) + "** ricercatori")
    if dt.days > 3 and st.button("Aggiorna"):
        with st.spinner():
            st.write("Aggiorna")

db.close()
#   streamlit run 0_Home.py