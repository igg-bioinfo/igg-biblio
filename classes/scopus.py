import pandas as pd
from datetime import datetime 
from classes.scopus_import import *
from classes.demo import *
from utils import *
import json

class Scopus:
    columns = ["doi", "pm_id", "issn", "title", "pub_date", "pub_type", "cited", "author_name", "author_scopus"]
    metrics_columns = ["hindex", "pubs", "allcited", "hindex5", "pubs5", "allcited5"]
    excel_columns = ["DOI", "PubMed", "ISSN", "Titolo", "Data", "Tipo", "Cit.", "Autore", "SCOPUS"]
    is_gaslini = None
    year = 0
    update_date = None
    update_days = None
    update_count_pubs = None
    update_count_authors = None
    min_days = 0


    #-----------------------------------GENERALI
    def __init__(self, st, db, year = None):
        self.st = st
        self.db = db
        self.year = datetime.now().year if year == None else year


    def manage_errors(self, scopus_type, failed, date_update):
        sql = "INSERT INTO scopus_failed (author_scopus, scopus_type, update_date, update_year) VALUES (%s, %s, %s)"
        for fail in failed:
            params = [scopus_type, fail[0], date_update, self.year]
            self.db.cur.execute(sql, params)


    def get_failed_details(self, scopus_type):
        with self.st.spinner():
            sql = "SELECT DISTINCT f.author_scopus, i.inv_name, f.update_date FROM scopus_failed f "
            sql += "INNER JOIN investigators i ON i.scopus_id = f.author_scopus "
            sql += "WHERE scopus_type = %s and f.update_year = %s ORDER BY i.inv_name"
            self.db.cur.execute(sql, [scopus_type, self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["SCOPUS ID", "Autore", "Aggiornamento fallito"])
            df.set_index('Autore', inplace=True)
            if len(df) > 0:
                self.st.dataframe(df)
                if self.st.button("Riprova ad importare le richieste fallite"):
                    for i, row in df.iterrows():
                        self.import_by_year(row["SCOPUS ID"])
                    self.st.experimental_rerun()
            

    def import_pubs(self, is_all, scopus = None):
        table = "scopus_pubs_all" if is_all else "scopus_pubs"
        filter =  "" if is_all else " AND PUBYEAR IS " + str(self.year) + " AND AFFIL(gaslini) "
        scopus_type = "all" if is_all else "by_year" 

        update_date = datetime.date(datetime.now())
        params = [self.year]
        sql = "DELETE FROM " + table + " WHERE update_year = %s"
        if scopus != None:
            sql += " and author_scopus = %s"
            params.append(scopus)
        self.db.cur.execute(sql, params)
        self.db.conn.commit()
        
        importer = Scopus_import(self.st, self.year)
        demo = Demo(self.st, self.db, self.year)
        scopus_invs = demo.get_all_from_db(True, False)
        df_invs = pd.DataFrame(scopus_invs, columns=demo.columns)
        authors_pubs = importer.get_authors_pubs(df_invs, filter, scopus)
        old_author_scopus = ""
        pubs = []
        author_pubs = None
        index = 1
        for author_pubs in authors_pubs:
            index += 1
            params = []
            sql_fields = "INSERT INTO " + table + " ("
            sql_values = ") VALUES ("
            for col in self.columns:
                value = author_pubs[col]
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
            self.st.success(sql_fields + sql_values)
            self.db.cur.execute(sql_fields + sql_values, params)
            self.db.cur.execute("DELETE FROM scopus_failed WHERE scopus_type = %s and update_year = %s and author_scopus = %s", 
                                [scopus_type, self.year, author_pubs["author_scopus"]])
            if is_all:
                if old_author_scopus not in ["", author_pubs["author_scopus"]]:
                    self.set_metrics(old_author_scopus, pubs, update_date)
                    pubs = []
                old_author_scopus = author_pubs["author_scopus"]
                pubs.append(author_pubs)
            
            self.db.conn.commit()
        if is_all and len(pubs) > 0:
            self.set_metrics(old_author_scopus, pubs, update_date)
            self.db.conn.commit()
        if importer.is_error():
            self.st.error(importer.error)
            self.manage_errors(scopus_type, importer.failed, update_date)
            self.db.conn.commit()
            return False


    #-----------------------------------PUBBLICAZIONI PER ANNO
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
        
    
    def import_pubs_by_year(self):
        if can_update(self.st, self) and self.st.button("Importa le pubblicazioni degli autori in anagrafica per il " + str(self.year), key="scopus_pubs_" + str(self.year)):
            #with self.st.spinner():
                self.import_pubs(False)
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
            download_excel(self.st, df, "scopus_pubs_" + str(self.year) + "_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            self.st.write(str(len(df)) + " Righe")
            self.st.dataframe(df, height=row_height)


    #-----------------------------------METRICHE
    def get_metrics_update_details(self):
        with self.st.spinner():
            sql = "SELECT update_date, COUNT(metric_id) FROM scopus_metrics WHERE "
            sql += "update_year = %s GROUP BY update_date "
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["update", "metrics"])
            if len(df) > 0:
                self.update_date = df["update"][0]
                self.update_count = df["metrics"][0]
                dt = datetime.date(datetime.now()) - self.update_date
                self.update_days = dt.days
                return True
        return False
        
    
    def import_metrics(self):
        if can_update(self.st, self) and self.st.button("Importa le metriche degli autori in anagrafica per il " + str(self.year), key="scopus_albo_" + str(self.year)):
            #with self.st.spinner():
                self.import_pubs(True)
                self.st.experimental_rerun()


    def sort_by_cited(self, e):
        return e["cited"]
    
    def get_condition(self, pub, is_all):
        pub_year = datetime.strptime(pub["pub_date"], '%Y-%m-%d').year
        last_5years = self.year - 5
        return (pub_year <= self.year) == False if is_all else (pub_year <= self.year and pub_year >= last_5years) == False
    
    def get_hindex(self, pubs, is_all):
        hindex = 0
        index = 1
        for p in pubs:
            if self.get_condition(p, is_all):
                continue
            if index > p["cited"]:
                break
            hindex = index
            index += 1
        return hindex
    
    def get_allcited(self, pubs, is_all):
        allcited = 0
        for p in pubs:
            if self.get_condition(p, is_all):
                continue
            allcited += p["cited"]
        return allcited
    
    def get_n_pubs(self, pubs, is_all):
        n_pubs = 0
        for p in pubs:
            if self.get_condition(p, is_all):
                continue
            n_pubs += 1
        return n_pubs

    def set_metrics(self, author_scopus, pubs: list, update_date):
        pubs.sort(key=self.sort_by_cited, reverse=True)

        hindex = self.get_hindex(pubs, True)
        n_pubs = self.get_n_pubs(pubs, True)
        allcited = self.get_allcited(pubs, True)

        hindex5 = self.get_hindex(pubs, False)
        n_pubs5 = self.get_n_pubs(pubs, False)
        allcited5 = self.get_allcited(pubs, False)

        sql = "UPDATE scopus_metrics SET hindex=%s, pubs=%s, allcited=%s, hindex5=%s, pubs5=%s, allcited5=%s, "
        sql += "update_date=%s WHERE author_scopus=%s and update_year = %s"
        self.db.cur.execute(sql, [hindex, n_pubs, allcited, hindex5, n_pubs5, allcited5, update_date, author_scopus, self.year])
        sql = "INSERT INTO scopus_metrics (author_scopus, hindex, pubs, allcited, hindex5, pubs5, allcited5, update_date, update_year) "
        sql += "SELECT %s, %s, %s, %s, %s, %s, %s, %s, %s "
        sql += "WHERE NOT EXISTS (SELECT 1 FROM scopus_metrics WHERE author_scopus = %s and update_year = %s)"
        self.db.cur.execute(sql, [author_scopus, hindex, n_pubs, allcited, hindex5, n_pubs5, allcited5, 
                                  update_date, self.year, author_scopus, self.year])


    #-----------------------------------ALBO
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
    
    def get_albo(self, only_scopus: bool = True):
        with self.st.spinner():
            sql = "SELECT i.inv_name, i.contract, " + age_field + ", CASE WHEN d.scopus_id IS NULL THEN i.scopus_id ELSE d.scopus_id END as scopus, "
            sql += (", ".join(self.metrics_columns)) + " "
            #sql += ", CASE WHEN hindex > 25 THEN 1 ELSE 0 END as PI "
            #sql += ", CASE WHEN hindex > 15 THEN 1 ELSE 0 END as CoPI "
            #sql += ", CASE WHEN " + age_field + " < 40 THEN 1 ELSE 0 END as Under40 "
            sql += "FROM investigators i "
            sql += "LEFT OUTER JOIN investigator_details d ON d.inv_name = i.inv_name "
            sql += "LEFT OUTER JOIN scopus_metrics ON (d.scopus_id IS NULL and author_scopus = i.scopus_id) or (d.scopus_id IS NOT NULL and author_scopus = d.scopus_id) "
            sql += "WHERE i.update_year = %s "
            if only_scopus:
                sql += " and (i.scopus_id IS NOT NULL or d.scopus_id IS NOT NULL) "
            sql += "ORDER BY (i.scopus_id IS NOT NULL or d.scopus_id IS NOT NULL), hindex is null, hindex DESC, " + age_field + " ASC, i.inv_name ASC"
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            albo_columns = ["Autore", "Contratto", "Età", "SCOPUS ID", "H-Index", "Pubs", "Cit.", "H-Index 5anni", "Pubs 5anni", "Cit. 5anni"]
            df = pd.DataFrame(res, columns=albo_columns)
            df["Email"] = ""
            for i, row in df.iterrows():
                df.loc[i, "Email"] = self.calculate_email(row["Autore"])

            download_excel(self.st, df, "albo_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            self.st.dataframe(df, height=row_height)