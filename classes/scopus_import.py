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
    max_res = 200


    def __init__(self, st, year):
        self.st = st
        self.year = year
    

    def is_error(self):
        return self.error != None


    def elsevier_request(self, function: str, params: str, start: int = 0):
        params += "&count=" + str(self.max_res) + "&apiKey=" + self.st.secrets["scopus_key"]
        if start != 0:
            params += "&start=" + str(start)
        params = params.replace(" ", "%20")
        url = 'https://api.elsevier.com/content/' + function + '?' + params
        try:
            response = requests.get(url, verify = True, proxies = self.proxies, headers={'Content-type': 'application/json'}, timeout = 25)
            return json.loads(response.content)
        except requests.exceptions.RequestException as e: 
            self.error = e
            return False 
    

    def get_pubs(self, author_name: str, author_scopus: str, filter: str = "", start: int = 0):
        params = "query=AU-ID(" + author_scopus + ")" + filter
        inv_pubs = self.elsevier_request("search/scopus", params, start)
        if inv_pubs == False:
            self.st.error("La richiesta per '" + author_scopus + "' ha prodotto il seguente errore:")
            self.st.error(self.error)
            self.error = None
            return False
        if "search-results" not in inv_pubs or "entry" not in inv_pubs["search-results"]:
            self.st.error("La richiesta per '" + author_scopus + "' non ha prodotto nessun risultato!")
            self.failed.append(author_scopus)
            return False
        pubs_total = 0 if "opensearch:totalResults" not in inv_pubs["search-results"] else int(inv_pubs["search-results"]["opensearch:totalResults"])
        pubs_count = len(inv_pubs["search-results"]["entry"])
        pubs = []
        for pub in inv_pubs["search-results"]["entry"]:    
            pub_dict = {}
            pub_dict["author_name"] = author_name
            pub_dict["author_scopus"] = author_scopus
            pub_dict["doi"] = pub["prism:doi"] if "prism:doi" in pub else None
            pub_dict["doi"] = pub["prism:doi"] if "prism:doi" in pub else None
            pub_dict["pm_id"] = pub["pubmed-id"] if "pubmed-id" in pub else None
            pub_dict["title"] = pub["dc:title"] if "dc:title" in pub else None
            pub_dict["issn"] = pub["prism:issn"] if "prism:issn" in pub else None
            pub_dict["pub_date"] = pub["prism:coverDate"] if "prism:coverDate" in pub else None
            pub_dict["pub_type"] = pub["subtypeDescription"] if "subtypeDescription" in pub else None #Erratum è da far fuori
            pub_dict["cited"] = int(pub["citedby-count"]) if "citedby-count" in pub else None
            pub_dict["pub_date"] = pub["prism:coverDate"] if "prism:coverDate" in pub else None
            pubs.append(pub_dict)
        return [pubs, start + pubs_count, pubs_total]


    def get_authors_pubs(self, df_scopus_invs, filter, scopus = None):
        progress_bar = self.st.progress(0,  text="Aggiornamento delle pubblicazioni")
        authors_pubs = []
        self.pub_count = 0
        self.failed = []
        percent_total = len(df_scopus_invs)
        for i, inv in df_scopus_invs.iterrows():
            author_name = inv["inv_name"]
            author_scopus = inv["scopus_id"]
            text = str(i) + " di " + str(percent_total) + " - Aggiornamento per " + author_name
            progress_bar.progress((i + 1) / percent_total, text=text)
            
            if scopus != None and author_scopus != scopus:
                continue
            
            pubs = []
            res = self.get_pubs(author_name, author_scopus, filter, 0)
            if res:
                for pub in res[0]:
                    pubs.append(pub)
                restart = res[1] 
                total = res[2]
                while restart < total:
                    res = self.get_pubs(author_name, author_scopus, filter, restart)
                    if res:
                        for pub in res[0]:
                            pubs.append(pub)
                        restart = res[1] 
                        total = res[2]
            for pub in pubs:
                authors_pubs.append(pub)   
        return authors_pubs