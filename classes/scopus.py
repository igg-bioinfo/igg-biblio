import pandas as pd
from datetime import datetime 
from classes.scopus_import import *
from classes.demo import *
from utils import *
import json

class Scopus:
    columns = ["doi", "pm_id", "issn", "title", "pub_date", "pub_type", "author_name", "author_scopus"]
    excel_columns = ["DOI", "PubMed", "ISSN", "Titolo", "Data", "Tipo", "Autore", "SCOPUS"]
    is_gaslini = None
    year = 0
    update_date = None
    update_days = None
    update_count_pubs = None
    update_count_authors = None
    min_days = 20


    def __init__(self, st, db, year = None):
        self.st = st
        self.db = db
        self.year = datetime.now().year if year == None else year


    def get_update_details(self):
        with self.st.spinner():
            sql = "SELECT update_date, COUNT(pub_authors) FROM scopus_pubs WHERE "
            sql += "update_year = %s "
            sql += "GROUP BY update_date, doi "
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["update", "authors"])
            if len(df) > 0:
                self.update_date = df["update"][0]
                self.update_count_pubs = len(df)
                self.update_count_authors = df["authors"].sum()
                dt = datetime.date(datetime.now()) - self.update_date
                self.update_days = dt.days
                return True
        return False
    

    def manage_errors(self, failed, date_update):
        sql = "INSERT INTO scopus_failed (author_scopus, update_date, update_year) VALUES (%s, %s, %s)"
        for fail in failed:
            params = [failed[0], date_update, self.year]
            self.db.cur.execute(sql, params)
            

    def import_exec(self, scopus = None):
        update_date = datetime.date(datetime.now())
        params = [self.year]
        sql = "DELETE FROM scopus_pubs WHERE update_year = %s"
        if scopus != None:
            sql += " and author_scopus = %s"
            params.append(scopus)
        self.db.cur.execute(sql, params)
        self.db.conn.commit()

        importer = Scopus_import(self.st, self.year)
        demo = Demo(self.st, self.db, self.year)
        scopus_invs = demo.get_all_from_db(True, False)
        df_invs = pd.DataFrame(scopus_invs, columns=demo.columns)
        for author in importer.get_author_pubs(df_invs, scopus):
            params = []
            sql_fields = "INSERT INTO scopus_pubs ("
            sql_values = ") VALUES ("
            for col in self.columns:
                value = author[col]
                if isinstance(value, str):
                    value = value.strip().title()
                elif isinstance(value, dict) or isinstance(value, list):
                    value = json.dumps(value)
                params.append(value)
                sql_fields += col + ", "
                sql_values += "%s, "
            params.append(update_date)
            params.append(self.year)
            sql_fields += "update_date, update_year"
            sql_values += "%s, %s)"
            self.db.cur.execute(sql_fields + sql_values, params)
            self.db.cur.execute("DELETE FROM scopus_failed WHERE update_year = %s and author_scopus = %s", [self.year, author["author_scopus"]])
        if importer.is_error():
            self.st.error(importer.error)
            self.manage_errors(importer.failed, update_date)
            return False
        self.db.conn.commit()
        
    
    def import_pubs(self):
        if can_update(self.st, self) and self.st.button("Importa le pubblicazioni degli autori in anagrafica", key="scopus_pubs_" + str(self.year)):
            with self.st.spinner():
                self.import_exec()
                self.st.experimental_rerun()


    def get_failed_details(self):
        with self.st.spinner():
            sql = "SELECT DISTINCT f.author_scopus, i.inv_name, f.update_date FROM scopus_failed f "
            sql += "INNER JOIN investigators i ON i.scopus_id = f.author_scopus "
            sql += "WHERE f.update_year = %s ORDER BY i.inv_name"
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["SCOPUS ID", "Autore", "Aggiornamento fallito"])
            df.set_index('Autore', inplace=True)
            if len(df) > 0:
                self.st.dataframe(df)
                if self.st.button("Riprova ad importare le richieste fallite"):
                    for i, row in df.iterrows():
                        self.import_exec(row["SCOPUS ID"])
                    self.st.experimental_rerun()


    def get_pubs_authors_for_year(self):
        with self.st.spinner():
            cols = ""
            for col in self.columns:
                cols += col + ", "
            cols = cols[:-2]
            sql = "SELECT " + cols + " FROM scopus_pubs WHERE "
            sql += "update_year = %s "
            if self.is_gaslini:
                sql += "AND is_gaslini = true "
            sql += "ORDER BY doi, pm_id "
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=self.excel_columns)
            df.set_index('Autore', inplace=True)
            download_excel(self.st, df, "scopus_author_pubs_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            self.st.write(str(len(df)) + " Righe")
            self.st.dataframe(df, height=666)