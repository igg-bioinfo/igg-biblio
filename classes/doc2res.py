import requests
from datetime import datetime 
import pandas as pd

class Doc2res:
    st = None
    year = 0
    headers = {}
    METHOD_CONTRACTS = 'contratti'
    METHOD_SURNAME = 'contratti/search'
    LIMIT = 500
    df = None
    rename_columns = {
        "COGNOME": "Cognome",
        "NOME": "Nome",
        "DATA_NASCITA": "Data di nascita",
        "EMAIL": "e-mail",
        "STRUTTURA": "Struttura23",
        "INVIARE_WFR": "EleggibilitàWF",
        "SITUAZIONE_CONTRATTUALE": "Situazione contrattuale",
        "DATA_FINE_CONTRATTO": "Data fine contratto vigente",
        "ORCID_ID": "ORCID",
        "RESEARCHER_ID": "ResearchID",
        "SCOPUS_AUTHOR_ID": "AuthorID Scopus"
    }


    def __init__(self, st, year = None):
        self.st = st
        self.year = datetime.now().year if year == None else year
        self.headers = {
            'Authorization': f'Bearer {self.st.secrets["doc2res_token"]}',
            'x-api-key': self.st.secrets["doc2res_token"],
            'Accept': 'application/json'
        }


    def get_all(self, import_columns):
        data = []
        offset = 0
        total = None
        api_url = self.st.secrets["doc2res_host"] + self.METHOD_CONTRACTS
        while total is None or offset < total:
            response = requests.get(
                api_url,
                headers=self.headers,
                params={
                    'offset': offset,
                    'limit': self.LIMIT
                },
                proxies={
                    "http": "http://fg-proxy-c.gaslini.lan:8080",
                    "https": "http://fg-proxy-c.gaslini.lan:8080"
                },
                timeout=(10, 20)
            )
            response.raise_for_status()
            chunk = response.json()

            chunk_data = chunk.get('data', [])
            if not isinstance(chunk_data, list):
                chunk_data = []
            if not chunk_data:
                break
            data.extend(chunk_data)
            pagination = chunk.get('pagination', {})
            if pagination.get('total') is not None:
                total = int(pagination['total'])
            else:
                if len(chunk_data) < self.LIMIT:
                    break
            offset += len(chunk_data)

        self.df = pd.DataFrame(data)
        self.df = self.df[self.df["ANNO_AFFILIAZIONE"] == self.year].copy()
        available_columns = [
            col for col in self.rename_columns
            if col in self.df.columns
        ]
        self.df = self.df[available_columns]
        self.df.rename(columns=self.rename_columns, inplace=True)
        self.df["e-mail2"] = self.df["e-mail"]
        self.df = self.df.map(
            lambda x: None if isinstance(x, str) and x.strip().lower() in ["none", "not available"] else x
        )