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
    year = 0
    update_date = None
    update_count = None
    update_days = None
    import_columns = ["Cognome","Data di nascita","Situazione contrattuale","SCOPUS ID"]
    columns = ["inv_name", "date_birth", "contract", "scopus_id"]
    excel_columns = ["Nome & Cognome", "Nascita", "Contratto", "SCOPUS", "Età"]
    min_days = 3


    def __init__(self, st, db, year = None):
        self.st = st
        self.db = db
        self.year = datetime.now().year if year == None else year

    def get_description(self):
        pass

    def get_update_details(self):
        with self.st.spinner():
            sql = "SELECT update_date, COUNT(inv_id) FROM investigators WHERE "
            sql += "update_year = %s GROUP BY update_date "
            self.db.cur.execute(sql,  [self.year])
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
        self.get_description()
        uploaded_file = self.st.file_uploader("**Importa un file excel per l'anagrafica che abbia le seguenti colonne: " + (", ".join(self.import_columns)) + "**", type=['.xlsx', '.xls'])
        if uploaded_file is not None:
            with self.st.spinner():
                self.import_excel(uploaded_file)
    

    def import_excel(self, excel):
        df_excel = pd.read_excel(excel)
        for col in self.import_columns:
            if col not in list(df_excel.columns):
                self.st.error("'" + col + "' non è una colonna valida")
                return False
            
        self.db.cur.execute("DELETE FROM pubmed_pubs WHERE update_year = %s;",  [self.year])
        self.db.conn.commit()
        
        sql_fields = "INSERT INTO investigators ("
        sql_values = ") VALUES ("
        for col in self.columns:
            sql_fields += col + ", "
            sql_values += "%s, "
        sql_fields += "update_date, update_year"
        sql_values += "%s, %s)"
        update_date = datetime.date(datetime.now())
        for i, row in df_excel.iterrows():
            params = []
            for col in self.import_columns:
                value = row[col]
                if value in ["N.A."]:
                    value = None
                elif isinstance(value, str):
                    value = value.strip().title()
                params.append(value)
            #inv_aliases is not present in excel
            params.append([])
            params.append(update_date)
            params.append(self.year)
            self.db.cur.execute(sql_fields + sql_values, params)
        self.db.conn.commit()
        self.st.experimental_rerun()
    

    def get_all_from_db(self, only_scopus = False, add_age = True):
        cols = ""
        for col in self.columns:
            if col == "scopus_id":
                cols += "CASE WHEN d.scopus_id IS NULL THEN i.scopus_id ELSE d.scopus_id END as scopus, "
            else:
                cols += "i." + col + ", "
        if add_age:
            cols += age_field + " as age "
        else:
            cols = cols[:-2]
        sql = "SELECT " + cols + "  FROM investigators i "
        sql += "LEFT OUTER JOIN investigator_details d ON d.inv_name = i.inv_name "
        sql += "WHERE i.update_year = %s "
        if only_scopus:
            sql += " and (i.scopus_id IS NOT NULL or d.scopus_id IS NOT NULL) "
        sql += "ORDER BY i.inv_name "
        self.db.cur.execute(sql, [self.year])
        res = self.db.cur.fetchall()
        return res


    def get_all(self):
        with self.st.spinner():
            res = self.get_all_from_db()
            df = pd.DataFrame(res, columns=self.excel_columns)
            df_grid = df.drop("Nascita", axis=1).set_index('Nome & Cognome')
            download_excel(self.st, df_grid, "investigators_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            self.st.dataframe(df_grid, height=row_height)