import pandas as pd
from datetime import datetime 
from utils import *

class User_request:
    user_name = ''
    first_name = ''
    last_name = ''
    contract = ''
    unit = ''
    scopus_id = ''
    orcid_id = ''
    researcher_id = ''
    year = 0
    update_date = None
    status = None
    inv_name = ''
    cols = ['email', 'first_name', 'last_name', 'contract', 'unit', 'scopus_id', 'orcid_id', 'researcher_id', 'update_date']

    def __init__(self, st, db):
        self.st = st
        self.db = db
        self.year = datetime.now().year 

    def get_requests(self, status):
        params = [status]
        sql = "SELECT " + ", ".join(self.cols) + " FROM investigator_requests WHERE status = %s "
        self.db.cur.execute(sql, params)
        res = self.db.cur.fetchall()
        df = pd.DataFrame(res, columns=self.cols)
        return df
    
    def dataframe_with_selections(self, df):
        df_with_selections = df.copy()
        df_with_selections.insert(0, "Seleziona", False)
        edited_df = self.st.data_editor(
            df_with_selections,
            hide_index=True,
            column_config={"Seleziona": self.st.column_config.CheckboxColumn(required=True)},
            disabled=df.columns,
        )
        selected_rows = edited_df[edited_df.Seleziona]
        return selected_rows.drop('Seleziona', axis=1)
    
    def update_status(self, status):
        sql = "UPDATE investigator_requests SET status = %s WHERE email = %s "
        self.db.cur.execute(sql, [status, self.user_name])
        self.db.conn.commit()


    def show_by_status(self, status):
        df = self.get_requests(status)
        if status == 0:
            self.st.markdown("#### Richieste in attesa di conferma")
            sel = self.dataframe_with_selections(df)
            if len(sel) > 0:
                self.update_date = sel.iloc[0]['update_date']
                self.user_name = sel.iloc[0]['email']
                self.first_name = sel.iloc[0]['first_name']
                self.last_name = sel.iloc[0]['last_name']
                self.contract = sel.iloc[0]['contract']
                self.unit = sel.iloc[0]['unit']
                self.scopus_id = sel.iloc[0]['scopus_id']
                self.orcid_id = sel.iloc[0]['orcid_id']
                self.researcher_id = sel.iloc[0]['researcher_id']
                #self.status = sel.iloc[0]['status']
                set_prop(self.st, "Data della richiesta", self.update_date)
                set_prop(self.st, "Email Gaslini / username", self.user_name)
                set_prop(self.st, "Nome", self.first_name)
                set_prop(self.st, "Cognome", self.last_name)
                set_prop(self.st, "Contratto", self.contract)
                set_prop(self.st, "Unità operativa", self.unit)
                set_prop(self.st, "SCOPUS ID", self.scopus_id)
                set_prop(self.st, "ORCID ID", self.orcid_id)
                set_prop(self.st, "Researcher ID", self.researcher_id)
                #set_prop(self.st, "Status", self.status)
                col_1, col_2 = self.st.columns([1,4])
                with col_1:
                    if self.st.button('Accetta la richiesta e crea un utente', key="request_accept"):
                        self.update_status(1)
                        self.st.experimental_rerun()
                with col_2:
                    if self.st.button('Rifiuta la richiesta', key="request_refused"):
                        self.update_status(2)
                        self.st.experimental_rerun()
        else:
            self.st.markdown("#### Richieste " + ("accettate" if status == 1 else "rifiutate"))
            show_df(self.st, df)