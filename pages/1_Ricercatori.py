import streamlit as st
from functions.utils import *
from classes.db_psql import *
from classes.user import *

title = "Ricercatori"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

with st.spinner():
    from datetime import datetime 
    import pandas as pd
    
    db.cur.execute('SELECT name, contract, date_birth, date_update FROM investigators WHERE date_update = (SELECT MAX(date_update) FROM investigators) ')
    res = db.cur.fetchall()
    df = pd.DataFrame(res, columns=["Nome & Cognome", "Contratto", "Nascita", "Aggiornamento"])
    print(df)
    df["Età"] = None
    for i, row in df.iterrows():
        print(row["Nascita"])
        if row["Nascita"] != None:
            dt = datetime.date(datetime.now()) - row["Nascita"]
            df["Età"] = int(dt.days / 365)
    df_grid = df[["Nome & Cognome", "Contratto", "Età"]].set_index('Nome & Cognome')
    st.dataframe(df_grid)

