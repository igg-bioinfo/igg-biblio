import pandas as pd
from datetime import datetime 
from utils import *

class Demo:
    st = None
    db = None
    id = 0
    name = ""
    user_name = ""
    user_type = ""
    update_date = None
    update_count = None
    update_days = None
    import_columns = ["Cognome","Data di nascita","Situazione contrattuale","SCOPUS ID"]


    def __init__(self, st, db):
        self.st = st
        self.db = db


    def get_update_details(self):
        set_msg_for_update(self.st, self)
        with self.st.spinner():
            self.db.cur.execute("SELECT date_update, count(inv_id) FROM investigators WHERE date_update = (SELECT MAX(date_update) FROM investigators) GROUP BY date_update")
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["update", "id"])
            if len(df) > 0:
                self.update_date = df["update"][0]
                self.update_count = df["id"][0]
                dt = datetime.date(datetime.now()) - self.update_date
                self.update_days = dt.days
                return True
        return False
    

    def upload_excel(self):
        uploaded_file = self.st.file_uploader("**Importa un file excel per l'anagrafica**", type=['.xlsx', '.xls'])
        if uploaded_file is not None:
            with self.st.spinner():
                self.import_excel(uploaded_file)
    

    def import_excel(self, excel):
        self.db.cur.execute("SELECT MAX(date_update) FROM investigators WHERE date_update < (SELECT MAX(date_update) FROM investigators)")
        res = self.db.cur.fetchall()
        df = pd.DataFrame(res, columns=["update"])
        if len(df) > 0 and df["update"][0] != None:
            self.db.cur.execute("DELETE FROM investigators WHERE date_update <= %s;",  [df["update"][0]])
            self.db.conn.commit()

        df_excel = pd.read_excel(excel)
        for col in self.import_columns:
            if col not in list(df_excel.columns):
                self.st.error("'" + col + "' non è una colonna valida")
                return False
        
        date_update = datetime.date(datetime.now())
        for i, row in df_excel.iterrows():
            params = []
            for col in self.import_columns:
                value = row[col]
                if value in ["N.A."]:
                    value = None
                if isinstance(value, str):
                    value = value.strip().title()
                params.append(value)
            params.append(date_update)
            self.db.cur.execute('INSERT INTO investigators (name, date_birth, contract, scopus_id, date_update) VALUES (%s, %s, %s, %s, %s)', params)
            self.db.conn.commit()
        self.st.experimental_rerun()
    

    def get_investigators(self):
        with self.st.spinner():
            self.db.cur.execute('SELECT name, contract, date_birth, scopus_id, date_update FROM investigators WHERE date_update = (SELECT MAX(date_update) FROM investigators) ')
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["Nome & Cognome", "Contratto", "Nascita", "SCOPUS", "Aggiornamento"])
            df["Età"] = None
            for i, row in df.iterrows():
                if row["Nascita"] != None:
                    dt = datetime.date(datetime.now()) - row["Nascita"]
                    row["Età"] = int(dt.days / 365)
                df.iloc[i] = row
            df_grid = df[["Nome & Cognome", "Contratto", "Età", "SCOPUS"]].set_index('Nome & Cognome')
            download_excel(self.st, df_grid, "investigators_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            self.st.dataframe(df_grid, height=666)