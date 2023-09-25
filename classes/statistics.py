import pandas as pd
from datetime import datetime 
from classes.scopus_import import *
from classes.demo import *
from utils import *
import json

class Statistics:

    no_units = "NESSUNA UO"

    #-----------------------------------GENERALI
    def __init__(self, st, db, year = None):
        self.st = st
        self.db = db
        self.year = datetime.now().year if year == None else year

    def select_units(self):
        sql = ""
        sql += "select distinct case when unit is null or unit = '' then '" + self.no_units + "' else unit end unit  "
        sql += "from view_invs i "
        sql += "where i.update_year = %s "
        sql += "order by unit "
        self.db.cur.execute(sql, [self.year])
        res = self.db.cur.fetchall()
        units = []
        for r in res:
            units.append(r[0])
        return self.st.selectbox('Unità selezionata:', units)
    
    def get_invs_by_unit(self, unit):
        params = [self.year]
        sql = ""
        sql += "select i.inv_name, i.age, i.scopus_id, "
        sql += "case when hindex is null then 0 else hindex end hindex, "
        sql += "case when hindex5 is null then 0 else hindex5 end hindex5, "
        sql += "case when hindex10 is null then 0 else hindex10 end hindex10, "
        sql += "case when i.date_end is null or i.date_end > now() then true else false end is_active "
        sql += "from view_invs i "
        sql += "left outer join scopus_metrics m on m.author_scopus = i.scopus_id "
        sql += "where i.update_year = %s and "
        if unit == self.no_units:
            sql += "unit is null or unit = '' "
        else:
            sql += "unit = %s "
            params.append(unit)
        sql += "order by unit "
        self.db.cur.execute(sql, params)
        res = self.db.cur.fetchall()
        df = pd.DataFrame(res, columns=["Ricercatore", "Età", "Scopus", "H-index 5", "H-index 10", "H-index", "In attività"])
        download_excel(self.st, df, "unit_" + datetime.now().strftime("%Y-%m-%d_%H.%M"), "_unit")
        show_df(self.st, df)

    def split_unit(self, df):
        df['Tipo unità'] = ''
        for i, row in df.iterrows():
            row = row.copy()
            split = row['Unità'].split(' (')
            df.loc[i, 'Unità'] = split[0]
            if len(split) > 1:
                df.loc[i, 'Tipo unità'] = split[1].replace(')', '')


    #-----------------------------------STATISTICHE
    def get_stats_units(self, filter_age = 0):
        sql = ""
        sql += "select * from ( "
        sql += "select case when unit is null or unit = '' then '" + self.no_units + "' else unit end unit, count(inv_name), "
        sql += "PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY hindex5) hindex5, "
        sql += "PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY hindex10) hindex10, "
        sql += "PERCENTILE_CONT(0.5) WITHIN GROUP(ORDER BY hindex) hindex "
        sql += "from ( select distinct i.inv_name, i.unit, i.scopus_id, "
        sql += "case when hindex is null then 0 else hindex end hindex, "
        sql += "case when hindex5 is null then 0 else hindex5 end hindex5, "
        sql += "case when hindex10 is null then 0 else hindex10 end hindex10 "
        sql += "from view_invs i "
        sql += "left outer join scopus_metrics m on m.author_scopus = i.scopus_id "
        sql += "where i.update_year = %s and (i.date_end is null or i.date_end > now()) "
        if filter_age > 0:
            sql += "and FLOOR((DATE_PART('day', now() - i.date_birth) / 365)::float) <= " + str(filter_age) + " "
        sql += ") f "
        #sql += "where f.scopus_id is not null " #f.unit is not null and
        sql += "group by unit "
        sql += ") f2 "
        sql += "order by hindex5 DESC, hindex10 DESC, hindex DESC "
        self.db.cur.execute(sql, [self.year])
        res = self.db.cur.fetchall()
        df = pd.DataFrame(res, columns=["Unità", "N° teste", "Media H-index 5", "Media H-index 10", "Media H-index"])
        self.split_unit(df)
        df = df[["Unità", 'Tipo unità', "N° teste", "Media H-index 5", "Media H-index 10", "Media H-index"]]
        filter_msg = " e con età minore o uguale a " + str(filter_age) if filter_age > 0 else ""
        self.st.markdown("### Metriche per unità" + filter_msg + "")
        filter_label = str(filter_age) + "_" if filter_age > 0 else ""
        download_excel(self.st, df, "stats_units_" + filter_label + datetime.now().strftime("%Y-%m-%d_%H.%M"), filter_label)
        show_df(self.st, df)

