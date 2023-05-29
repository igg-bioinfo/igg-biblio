import pandas as pd
from datetime import datetime 
from classes.scopus_import import *
from classes.demo import *
from utils import *
import json

class Scopus:
    columns = ["eid", "doi", "pm_id", "issn", "title", "pub_date", "pub_type", "cited", "author_name", "author_scopus"]
    metrics_columns = ["pubs", "allcited", "hindex", "pubs5", "allcited5", "hindex5"]
    excel_columns = ["EID", "DOI", "PubMed", "ISSN", "Titolo", "Data", "Tipo", "Cit.", "Autore", "SCOPUS"]
    is_gaslini = None
    year = 0
    update_date = None
    update_days = None
    update_count_pubs = None
    update_count_authors = None
    metrics_update = []
    min_days = 20
    max_pucs = 100


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
        progress_bar = self.st.progress(0,  text="Aggiornamento del database")
        percent_total = len(authors_pubs)
        i = 1
        for author_pubs in authors_pubs:
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
            self.db.cur.execute(sql_fields + sql_values, params)
            self.db.cur.execute("DELETE FROM scopus_failed WHERE scopus_type = %s and update_year = %s and author_scopus = %s", 
                                [scopus_type, self.year, author_pubs["author_scopus"]])
            text = "Aggiornamento dati per " + author_pubs["author_name"]
            progress_bar.progress(i / percent_total, text=text)
            if is_all:
                if old_author_scopus not in ["", author_pubs["author_scopus"]]:
                    self.set_metrics(old_author_scopus, pubs, update_date)
                    text = "Aggiornamento metriche per " + author_pubs["author_name"]
                    progress_bar.progress(i / percent_total, text=text)
                    pubs = []
                old_author_scopus = author_pubs["author_scopus"]
                pubs.append(author_pubs)
            
            self.db.conn.commit()
            i += 1
        if is_all and len(pubs) > 0:
            self.set_metrics(old_author_scopus, pubs, update_date)
            text = "Aggiornamento metriche per " + author_pubs["author_name"]
            progress_bar.progress((i - 1) / percent_total, text=text)
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
            sql = "SELECT " + cols + " FROM scopus_pubs  "
            sql += "WHERE update_year = %s "
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
            sql = "SELECT update_date, COUNT(metric_id) FROM scopus_metrics "
            sql += "WHERE update_year = %s GROUP BY update_date ORDER BY update_date DESC"
            self.db.cur.execute(sql, [self.year])
            res = self.db.cur.fetchall()
            df = pd.DataFrame(res, columns=["update", "metrics"])
            self.metrics_update = []
            for i, row in df.iterrows():
                self.metrics_update.append({"update": row["update"], "metrics": row["metrics"]})
            if len(df) > 0:
                self.update_date = df["update"][0]
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


    #-----------------------------------PUC
    def import_pucs(self, scopus = None):
        params = [self.year]
        sql = "SELECT eid "
        sql += "FROM scopus_pubs_all "
        sql += "WHERE update_year = %s "
        if scopus != None:
            sql += " and author_scopus = %s "
            params.append(scopus)
        sql += "and eid NOT IN (SELECT DISTINCT eid FROM scopus_pucs) LIMIT " + str(self.max_pucs)
        self.db.cur.execute(sql, params)
        res = self.db.cur.fetchall()
        if res:
            fields = ""
            values = ""
            for f in range(1, 3):
                fields += "first" + str(f) + ", last" + str(f) + ", "
                values += "%s, %s, "
            for f in range(1, 5):
                fields += "corr" + str(f) + ", "
                values += "%s, "
            sql = "INSERT INTO scopus_pucs (eid, " + fields + " pub_year) "
            sql += "SELECT %s, " + values + " %s "
            importer = Scopus_import(self.st, self.year)
            for r in res:
                puc = importer.get_puc(r[0])
                params = [puc["eid"]]
                for f in range(1, 3):
                    params.append(puc["first" + str(f)])
                    params.append(puc["last" + str(f)])
                for f in range(1, 5):
                    params.append(puc["corr" + str(f)])
                params.append(puc["pub_year"])
                self.db.cur.execute(sql, params)
                self.db.conn.commit()
        self.st.experimental_rerun()



    #-----------------------------------ALBO
    def get_albo(self, only_scopus: bool = True):
        with self.st.spinner():
            sql = ""
            sql += "SELECT l.*, COUNT(c.eid) as corrs FROM ( "
            sql += "SELECT f.*, COUNT(l.eid) as lasts FROM ( "
            sql += "SELECT s.*, COUNT(f.eid) as firsts FROM ( "
            sql += "SELECT i.inv_name, i.contract, " + age_field + " as age, CASE WHEN d.scopus_id IS NULL THEN i.scopus_id ELSE d.scopus_id END as scopus, "
            sql += (", ".join(self.metrics_columns)) + ", "
            sql += "(CASE WHEN pubs - (CASE WHEN pubs_puc IS NULL THEN 0 ELSE pubs_puc END) > 0 THEN (CASE WHEN pubs_puc IS NULL THEN 0 ELSE pubs_puc END)::text ELSE (CASE WHEN pubs IS NULL OR pubs = 0 THEN 'Nessun dato' ELSE 'OK' END) END) as puc "
            sql += "FROM investigators i "
            sql += "LEFT OUTER JOIN investigator_details d ON d.inv_name = i.inv_name "
            sql += "LEFT OUTER JOIN scopus_metrics m ON (d.scopus_id IS NULL and m.author_scopus = i.scopus_id) or (d.scopus_id IS NOT NULL and m.author_scopus = d.scopus_id) "
            sql += "LEFT OUTER JOIN (select author_scopus, count(eid) as pubs_puc from scopus_pubs_all WHERE update_year = %s and eid IN (SELECT DISTINCT eid FROM scopus_pucs) group by author_scopus) p "
            sql += "ON (d.scopus_id IS NULL and p.author_scopus = i.scopus_id) or (d.scopus_id IS NOT NULL and p.author_scopus = d.scopus_id) "
            sql += "WHERE i.update_year = %s "
            if only_scopus:
                sql += " and (i.scopus_id IS NOT NULL or d.scopus_id IS NOT NULL) "
            sql += ") s "
            sql += "LEFT OUTER JOIN scopus_pucs f on (s.scopus = f.first1 or s.scopus = f.first2 or s.scopus = f.first3) "
            sql += "GROUP BY inv_name, contract, age, scopus, " + (", ".join(self.metrics_columns)) + ", puc "
            sql += ") f "
            sql += "LEFT OUTER JOIN scopus_pucs l on (f.scopus = l.last1 or f.scopus = l.last2 or f.scopus = l.last3) "
            sql += "GROUP BY inv_name, contract, age, scopus, " + (", ".join(self.metrics_columns)) + ", puc, firsts "
            sql += ") l "
            sql += "LEFT OUTER JOIN scopus_pucs c on (l.scopus = c.corr1 or l.scopus = c.corr2 or l.scopus = c.corr3 or l.scopus = c.corr4 or l.scopus = c.corr5) "
            sql += "GROUP BY inv_name, contract, age, scopus, " + (", ".join(self.metrics_columns)) + ", puc, firsts, lasts "
            sql += "ORDER BY hindex is null, hindex DESC, age ASC, inv_name ASC "
            #self.st.success(sql)
            self.db.cur.execute(sql, [self.year, self.year])
            res = self.db.cur.fetchall()
            albo_columns = ["Autore", "Contratto", "Età", "SCOPUS ID", "Pubs", "Cit.", "H-Index", "Pubs 5 anni", "Cit. 5 anni", "H-Index 5 anni", "Pubs con PUC", "Primi", "Ultimi", "Corr."]
            df = pd.DataFrame(res, columns=albo_columns)
            df["Email"] = ""
            for i, row in df.iterrows():
                df.loc[i, "Email"] = calculate_email(row["Autore"])

            download_excel(self.st, df, "albo_" + datetime.now().strftime("%Y-%m-%d_%H.%M"))
            self.st.dataframe(df, height=row_height)