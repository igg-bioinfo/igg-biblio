import pandas as pd
from datetime import datetime 
from classes.pubmed_import import *
from utils import *
import json

class Pubmed:
    columns = ["author_orcid",
        "author_name",
        "is_person",
        "position",
        "corresponding",
        "pm_id",
        "journal",
        "issn",
        "title",
        "pub_date",
        "pmc_id",
        "affiliations"]
    excel_columns = ["ORCID",
        "Autore",
        "Persona",
        "Posizione",
        "Corresponding",
        "PUBMED",
        "Rivista",
        "ISSN",
        "Titolo",
        "Data",
        "PMC",
        "Affiliazioni"]
    is_gaslini = None
    year = 0
    update_date = None
    update_days = None
    update_count_authors = None
    update_count_pubs = None

    def __init__(self, st, db, is_gaslini = True, year = None):
        self.st = st
        self.db = db
        self.is_gaslini = is_gaslini
        self.year = datetime.now().year if year == None else year


    def get_update_details(self):
        with self.st.spinner():
            sql = "SELECT date_update, COUNT(author_pub_id) FROM pubs_pubmed WHERE "
            if self.is_gaslini:
                sql += "lower(affiliations::text) like '%%gaslini%%' and "
            sql += "date_year = %s GROUP BY date_update, pm_id "
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["update", "id"])
            if len(df) > 0:
                self.update_date = df["update"][0]
                self.update_count_pubs = len(df)
                self.update_count_authors = df["id"].sum()
                dt = datetime.date(datetime.now()) - self.update_date
                self.update_days = dt.days
                return True
        return False
    
    def import_pubs(self):
        set_msg_for_update(self.st, self)
        if self.update_days != None:
            self.st.success("E' possibile aggiornare i dati")
        if self.st.button("Importa le pubblicazioni e relativi autori", key="pubs_" + str(self.year)):
            with self.st.spinner():
                date_update = datetime.date(datetime.now())
                self.db.cur.execute("DELETE FROM pubs_pubmed WHERE date_year = %s;",  [self.year])
                self.db.conn.commit()
                importer = Pubmed_import(self.st, self.year)
                for pub in importer.get_data():
                    for author in pub["authors"]:
                        params = []
                        sql_fields = "INSERT INTO pubs_pubmed ("
                        sql_values = ") VALUES ("
                        for col in self.columns:
                            value = author[col] if col in author else pub[col]
                            if isinstance(value, str):
                                value = value.strip().title()
                            elif isinstance(value, dict) or isinstance(value, list):
                                value = json.dumps(value)
                            
                            params.append(value)
                            sql_fields += col + ", "
                            sql_values += "%s, "
                        params.append(date_update)
                        params.append(self.year)
                        sql_fields += "date_update, date_year"
                        sql_values += "%s, %s)"
                        self.db.cur.execute(sql_fields + sql_values, params)
                if importer.is_error():
                    self.st.error(importer.error)
                    return False
                self.db.conn.commit()
                self.st.experimental_rerun()


    def get_authors_pubs_for_year(self):
        with self.st.spinner():
            cols = ""
            for col in self.columns:
                cols += col + ", "
            cols = cols[:-2]
            sql = "SELECT " + cols + " FROM pubs_pubmed WHERE "
            if self.is_gaslini:
                sql += "lower(affiliations::text) like '%%gaslini%%' and "
            sql += "date_year = %s ORDER BY pub_date, pm_id, position "
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=self.excel_columns)
            df.set_index('Autore', inplace=True)
            download_excel(self.st, df, "all_authors_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            self.st.write(str(len(df)) + " Righe")
            self.st.dataframe(df, height=666)
