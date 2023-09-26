import pandas as pd
import json
from datetime import datetime 
from classes.pubmed_import import *
from utils import *

class Pubmed:
    st = None
    db = None
    pubs_cols_n = 7
    columns = [
        "pm_id",
        "doi",
        "journal",
        "issn",
        "title",
        "pub_date",
        "pmc_id",
        "author_orcid",
        "author_name",
        "is_person",
        "position",
        "corresponding",
        "affiliations"]
    excel_columns = [
        "PUBMED",
        "DOI",
        "Rivista",
        "ISSN",
        "Titolo",
        "Data",
        "PMC",
        "ORCID",
        "Autore",
        "Persona",
        "Posizione",
        "Corresponding",
        "Affiliazioni"]
    is_gaslini = None
    year = 0
    update_date = None
    update_days = None
    update_count_authors = None
    update_count_pubs = None
    min_days = min_pubmed


    def __init__(self, st, db, is_gaslini = True, year = None):
        self.st = st
        self.db = db
        self.is_gaslini = is_gaslini
        self.year = datetime.now().year if year == None else year


    def get_update_details(self):
        with self.st.spinner():
            sql = "SELECT update_date, COUNT(pub_authors) FROM pubmed_pubs WHERE "
            if self.is_gaslini:
                sql += "lower(affiliations::text) like '%%gaslini%%' and "
            sql += " EXTRACT('Year' from TO_DATE(pub_date,'YYYY-MM-DD')) = %s GROUP BY update_date, pm_id "
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
    
    def import_pubs_by_year(self):
        if can_update(self.st, self) and self.st.button("Importa le pubblicazioni e relativi autori", key="pubmed_pubs_" + str(self.year)):
            with self.st.spinner():
                update_date = datetime.date(datetime.now())
                self.db.cur.execute("DELETE FROM pubmed_pubs WHERE update_year = %s;",  [self.year])
                self.db.conn.commit()
                importer = Pubmed_import(self.st, self.year)
                for pub in importer.get_pubs():
                    for author in pub["authors"]:
                        params = []
                        sql_fields = "INSERT INTO pubmed_pubs ("
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
                        params.append(update_date)
                        params.append(self.year)
                        sql_fields += "update_date, update_year"
                        sql_values += "%s, %s)"
                        self.db.cur.execute(sql_fields + sql_values, params)
                if importer.is_error():
                    self.st.error(importer.error)
                    return False
                self.db.conn.commit()
                self.st.experimental_rerun()


    def get_pubs_authors_for_year(self):
        with self.st.spinner():
            cols_pub = self.columns[:self.pubs_cols_n]
            excel_cols_pub = self.excel_columns[:self.pubs_cols_n]
            cols = ""
            for col in cols_pub:
                cols += col + ", "
            cols = cols[:-2]
            sql = "SELECT DISTINCT " + cols + " FROM pubmed_pubs WHERE "
            if self.is_gaslini:
                sql += "lower(affiliations::text) like '%%gaslini%%' and "
            sql += " EXTRACT('Year' from TO_DATE(pub_date,'YYYY-MM-DD')) = %s ORDER BY pub_date DESC, pm_id "
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=excel_cols_pub)
            download_excel(self.st, df, "pubmed_author_pubs_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            show_df(self.st, df)


    def get_no_scopus_pubs_author_for_year(self, author, scopus_id):
        with self.st.spinner():
            cols_pub = self.columns[:self.pubs_cols_n]
            excel_cols_pub = self.excel_columns[:self.pubs_cols_n]
            cols = ""
            for col in cols_pub:
                cols += col + ", "
            cols = cols[:-2]
            sql = "SELECT DISTINCT " + cols + " FROM pubmed_pubs WHERE pm_id in ("
            sql += "select pm_id from pubs_not_in_scopus_per_author(%s, %s)" #pubs_not_in_scopus(%s)
            sql += ") and author_name like '%%" + author + "%%' and EXTRACT('Year' from TO_DATE(pub_date,'YYYY-MM-DD')) = %s "
            sql += "ORDER BY pub_date DESC, pm_id "
            self.db.cur.execute(sql, [self.year, scopus_id, self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=excel_cols_pub)
            download_excel(self.st, df, "pubmed_author_pubs_" + datetime.now().strftime("%Y-%m-%d_%H.%M"), 'no_scopus_pubmed_pubs')
            show_df(self.st, df)

    def get_no_scopus_pubs_authors_for_year(self):
        with self.st.spinner():
            cols_pub = self.columns[:self.pubs_cols_n]
            excel_cols_pub = self.excel_columns[:self.pubs_cols_n]
            cols = ""
            for col in cols_pub:
                cols += col + ", "
            cols = cols[:-2]
            sql = "SELECT DISTINCT " + cols + " FROM pubmed_pubs WHERE pm_id in ("
            sql += "select pm_id from pubs_not_in_scopus(%s)"
            sql += ") and EXTRACT('Year' from TO_DATE(pub_date,'YYYY-MM-DD')) = %s "
            sql += "ORDER BY pub_date DESC, pm_id "
            self.db.cur.execute(sql, [self.year, self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=excel_cols_pub)
            download_excel(self.st, df, "pubmed_author_pubs_" + datetime.now().strftime("%Y-%m-%d_%H.%M"), 'no_scopus_pubmed_pubs')
            show_df(self.st, df)
