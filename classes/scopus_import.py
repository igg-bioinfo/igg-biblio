from datetime import datetime 
from utils import *
import requests
import json

class Scopus_import:
    st = None
    proxies = {
    'http': 'http://fg-proxy-c.gaslini.lan:8080',
    'https': 'http://fg-proxy-c.gaslini.lan:8080',
    }
    error = None
    failed = []


    def __init__(self, st, year):
        self.st = st
        self.year = year
    

    def is_error(self):
        return self.error != None


    def elsevier_request(self, function: str, params: str):
        params += "&count=200&apiKey=" + self.st.secrets["scopus_key"]
        params = params.replace(" ", "%20")
        url = 'https://api.elsevier.com/content/' + function + '?' + params
        try:
            response = requests.get(url, verify = True, proxies = self.proxies, headers={'Content-type': 'application/json'}, timeout = 5)
            return json.loads(response.content)
        except requests.exceptions.RequestException as e: 
            self.error = e
            return False 


    def get_author_pubs(self, df_scopus_invs, scopus = None):
        pubs = []
        self.pub_count = 0
        self.failed = []
        function = "search/scopus"
        for i, inv in df_scopus_invs.iterrows():
            author_name = inv["inv_name"]
            author_scopus = inv["scopus_id"]
            if scopus != None and author_scopus != scopus:
                continue
            params = "query=AU-ID(" + author_scopus + ") AND PUBYEAR IS " + str(self.year) + " AND AFFIL(gaslini) "
            inv_pubs = self.elsevier_request(function, params)
            if inv_pubs == False:
                self.st.error("La richiesta per '" + author_name + "' ha prodotto il seguente errore:")
                self.st.error(self.error)
                self.error = None
                continue
            if "search-results" not in inv_pubs or "entry" not in inv_pubs["search-results"]:
                self.st.error("La richiesta per '" + author_name + "' non ha prodotto nessun risultato!")
                self.failed.append(author_scopus)
                continue
            for pub in inv_pubs["search-results"]["entry"]:    
                author_dict = {}
                author_dict["doi"] = pub["prism:doi"] if "prism:doi" in pub else None
                if author_dict["doi"] == None:
                    continue
                author_dict["pm_id"] = pub["pubmed-id"] if "pubmed-id" in pub else None
                author_dict["title"] = pub["dc:title"] if "dc:title" in pub else None
                author_dict["issn"] = pub["prism:issn"] if "prism:issn" in pub else None
                author_dict["pub_date"] = pub["prism:coverDate"] if "prism:coverDate" in pub else None
                author_dict["pub_type"] = pub["subtypeDescription"] if "subtypeDescription" in pub else None #Erratum è da far fuori
                author_dict["author_name"] = author_name
                author_dict["author_scopus"] = author_scopus
                pubs.append(author_dict)
        return pubs