import pandas as pd
from datetime import datetime 
from utils import *
from classes.user import *

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
    update_count_filter = None
    update_days = None
    #import_columns = ["Cognome","Data di nascita","Situazione contrattuale","SCOPUS ID"]
    import_columns = ["Cognome", "Nome", "Data di nascita", "e-mail", "e-mail2", "Struttura23",
                      "EleggibilitàWF", "Situazione contrattuale", "Data fine contratto vigente",
                      "ORCID", "ResearchID", "AuthorID Scopus"]
    #columns = ["inv_name", "date_birth", "contract", "scopus_id"]
    columns = ["last_name", "first_name", "date_birth", "user_name", "email2", "unit",
               "is_workflow", "contract", "date_end",
               "orcid_id", "researcher_id", "scopus_id", "age"]
    #excel_columns = ["Nome & Cognome", "Nascita", "Contratto", "SCOPUS", "Età"]
    excel_columns = ["Nome & Cognome", "Cognome", "Nome", "Nascita", "Email", "Email2", "Unità",
               "Workflow", "Contratto", "Data fine contratto",
               "ORCID ID", "RESEARCHER ID", "SCOPUS ID", "Età"]
    min_days = 3


    def __init__(self, st, db, year = None):
        self.st = st
        self.db = db
        self.year = datetime.now().year if year == None else year

    def get_description(self):
        pass

    def get_update_details(self):
        with self.st.spinner():
            sql = "SELECT DISTINCT update_date, COUNT(inv_name) FROM investigators WHERE "
            sql += "update_year = %s GROUP BY update_date ORDER BY update_date DESC "
            self.db.cur.execute(sql,  [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["update", "id"])
            if len(df) > 0:
                self.update_date = df["update"][0]
                self.update_count = df["id"][0]
                dt = datetime.date(datetime.now()) - self.update_date
                self.update_days = dt.days
                res1 = self.get_all_from_db(True)
                self.update_count_filter = len(res1)
                return True
        return False
    

    def upload_excel(self):
        self.get_description()
        with self.st.form("upload-form", clear_on_submit=True):
            uploaded_file = self.st.file_uploader("**Importa un file excel per l'anagrafica che abbia le seguenti colonne: " + 
                                              (", ".join(self.import_columns)) + "**", type=['.xlsx', '.xls'])
            submitted = self.st.form_submit_button("Importa file")

        if submitted and uploaded_file is not None:
            with self.st.spinner():
                self.import_excel(uploaded_file)
                self.st.experimental_rerun()


    def import_excel(self, excel):
        df_excel = pd.read_excel(excel)
        for col in self.import_columns:
            if col not in list(df_excel.columns):
                self.st.error("'" + col + "' non è una colonna valida")
                return False
        self.db.cur.execute("DELETE FROM investigators WHERE update_year = %s;",  [self.year])
        self.db.conn.commit()
        self.create_sql2(df_excel)


    def create_sql2(self, df_excel):
        sql_fields = "INSERT INTO investigators (inv_name, "
        sql_values = ") VALUES (%s, "
        for col in self.columns:
            if col != "age":
                sql_fields += ("email" if col == "user_name" else col) + ", "
                sql_values += "%s, "
        sql_fields += "update_date, update_year"
        sql_values += "%s, %s, %s)"
        update_date = datetime.date(datetime.now())
        for i, row in df_excel.iterrows():
            name = row["Cognome"].strip().title() + " " + row["Nome"].strip().title()
            params = [name]
            for col in self.import_columns:
                value = row[col]
                if str(value) in ["N.A.", "N.A", "nan"]:
                    value = None
                elif "e-mail" in col or col in ["ORCID", "ResearchID", "AuthorID Scopus"]:
                    value = value.strip().lower()
                elif col == "EleggibilitàWF":
                    value = True if str(value).upper() in ['TRUE', '1'] else False
                elif isinstance(value, str):
                    value = value.strip().title()
                params.append(value)
            params.append(update_date)
            params.append(self.year)
            #self.st.success(sql_fields + sql_values)
            #self.st.success(params)
            self.db.cur.execute(sql_fields + sql_values, params)
            self.db.conn.commit()
            user = User(self.st, self.db, name)
            user.insert_new()
        self.db.close()
        self.db.connect()
    

    def get_all_from_db(self, only_scopus = False):
        cols = ""
        for col in self.columns:
            cols += "i." + col + ", "
        cols = cols[:-2]
        sql = "SELECT i.inv_name, " + cols + "  FROM view_invs i "
        sql += "WHERE i.update_year = %s "
        if only_scopus:
            sql += " and i.scopus_id IS NOT NULL "
        sql += "ORDER BY i.inv_name "
        self.db.cur.execute(sql, [self.year])
        res = self.db.cur.fetchall()
        return res


    def get_all(self):
        with self.st.spinner():
            res = self.get_all_from_db()
            df = pd.DataFrame(res, columns=self.excel_columns, index=None)
            df_grid = df.drop("Nascita", axis=1).drop("Workflow", axis=1).reset_index(drop=True)
            download_excel(self.st, df_grid, "investigators_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            show_df(self.st, df_grid)