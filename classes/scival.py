import pandas as pd
from datetime import datetime 
from classes.scival_import import *
from utils import *

class Scival:
    year = 0
    max_reqs = 20
    update_date = None
    update_days = None
    update_count = None
    min_days = 20
    age_calc = " FLOOR((DATE_PART('day', now() - i.date_birth) / 365)::float) "

    def __init__(self, st, db, year = None):
        self.st = st
        self.db = db
        self.year = year

    def get_update_details(self):
        with self.st.spinner():
            sql = "SELECT update_date, COUNT(metric_id) FROM scival_hindex WHERE "
            sql += "update_year = %s GROUP BY update_date "
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["update", "h-index"])
            if len(df) > 0:
                self.update_date = df["update"][0]
                self.update_count = df["h-index"][0]
                dt = datetime.date(datetime.now()) - self.update_date
                self.update_days = dt.days
                return True
        return False
    
    def update_authors(self, json):
        if "results" in json:
            for metric in json["results"]:
                hindex = None
                scopus = None
                if "metrics" in metric and "value" in metric["metrics"][0]:
                    hindex = metric["metrics"][0]["value"]
                if hindex != None and "author" in metric and "id" in metric["author"]:
                    scopus = metric["author"]["id"]
                if hindex != None and scopus != None:
                    sql = "UPDATE scival_hindex SET author_hindex=%s, update_date=%s, update_year=%s WHERE author_scopus='%s'"
                    self.db.cur.execute(sql, [hindex, self.update_date, self.year, scopus])
                    sql = "INSERT INTO scival_hindex (author_hindex, author_scopus, update_date, update_year) SELECT %s, '%s', '%s', %s "
                    sql += "WHERE NOT EXISTS (SELECT 1 FROM scival_hindex WHERE author_scopus = '%s')"
                    self.db.cur.execute(sql, [hindex, scopus, self.update_date, self.year, scopus])
                    self.db.conn.commit() 

    def import_metrics(self):
        if can_update(self.st, self) and self.st.button("Aggiorna H-Indexes"):
            with self.st.spinner():
                self.update_date = datetime.date(datetime.now())
                importer = Scival_import(self.st)
                df = self.get_all_from_db(True)
                index = 0
                authors = ""
                for i, row in df.iterrows():
                    authors += row["SCOPUS ID"] + ","
                    if index < self.max_reqs:
                        index += 1
                    else: 
                        authors = authors[:-1]
                        json = importer.get_hindex(authors)
                        if json:
                            self.update_authors(json)
                        authors = ""
                        index = 0
                if authors != "":
                    authors = authors[:-1]
                    json = importer.get_hindex(authors)
                    if json:
                        self.update_authors(json)


    def get_all_from_db(self, only_scopus = False):
        sql = "SELECT i.scopus_id, i.inv_name, i.contract, " + self.age_calc + " as age, sh.author_hindex "
        sql += ", CASE WHEN sh.author_hindex > 25 THEN 1 ELSE 0 END as PI "
        sql += ", CASE WHEN sh.author_hindex > 15 THEN 1 ELSE 0 END as CoPI "
        sql += ", CASE WHEN " + self.age_calc + " < 40 THEN 1 ELSE 0 END as Under40 "
        sql += "FROM investigators i "
        sql += "LEFT OUTER JOIN scival_hindex sh ON i.scopus_id = sh.author_scopus "
        sql += "WHERE i.update_year = %s "
        if only_scopus:
            sql += " and scopus_id IS NOT NULL "
        sql += "ORDER BY i.scopus_id is null, sh.author_hindex is null, sh.author_hindex DESC, " + self.age_calc + " ASC, i.inv_name ASC"
        self.db.cur.execute(sql, [self.year])
        res = self.db.cur.fetchall()
        df = pd.DataFrame(res, columns=["SCOPUS ID", "Autore", "Contratto", "Età", "H-Index", "El. PI", "El. Co-PI", "Under 40"])
        return df
    
    def calculate_email(self, author):
        author_email = ""
        author_array = str(author).lower().split(" ")
        if len(author_array) > 2:
            if len(author_array[0]) > 3:
                author_email = author_array[1] + author_array[0]
            else:
                author_email = author_array[2] + author_array[0] + author_array[1]
        elif len(author_array) > 1:
            author_email = author_array[1] + author_array[0]
        else:
            author_email = author_array[0]
        author_email += "@gaslini.org"
        author_email = strip_accents(author_email)
        return author_email

    def get_albo(self, only_scopus = False):
        with self.st.spinner():
            df = self.get_all_from_db(only_scopus)
            df["Email"] = ""
            for i, row in df.iterrows():
                df.loc[i, "Email"] = self.calculate_email(row["Autore"])

            download_excel(self.st, df, "albo_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            self.st.dataframe(df, height=666)