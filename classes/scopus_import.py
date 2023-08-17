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
    eid_prefix = "2-S2.0-"


    #-----------------------------------GENERALI
    def __init__(self, st, year):
        self.st = st
        self.year = year
    

    def is_error(self):
        return self.error != None


    def elsevier_request(self, function: str, params: str, start: int = 0):
        params += ("" if params == "" else "&") + "count=" + str(self.max_res) + "&apiKey=" + self.st.secrets["scopus_key"]
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


    #-----------------------------------PUBBLICAZIONI
    def get_pubs_for_range(self, author_name: str, author_scopus: str, filter: str = "", start: int = 0):
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
            pub_dict["eid"] = pub["eid"] if "eid" in pub else None
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
        progress_bar = self.st.progress(0, text="Inizializzazione del recupero delle pubblicazioni")
        authors_pubs = []
        self.pub_count = 0
        self.failed = []
        percent_total = len(df_scopus_invs)
        for i, inv in df_scopus_invs.iterrows():
            author_name = inv["inv_name"]
            author_scopus = inv["scopus_id"]
            
            if scopus != None and author_scopus != scopus:
                continue
            text = "1 di 1" if scopus != None else str(i) + " di " + str(percent_total) 
            text = text + " - Recupero delle pubblicazioni di " + author_name
            progress_bar.progress((i + 1) / percent_total, text=text)
            
            pubs = []
            res = self.get_pubs_for_range(author_name, author_scopus, filter, 0)
            if res:
                for pub in res[0]:
                    pubs.append(pub)
                restart = res[1] 
                total = res[2]
                while restart < total:
                    res = self.get_pubs_for_range(author_name, author_scopus, filter, restart)
                    if res:
                        for pub in res[0]:
                            pubs.append(pub)
                        restart = res[1] 
                        total = res[2]
            for pub in pubs:
                authors_pubs.append(pub)   
        return authors_pubs


    #-----------------------------------PUC
    def get_puc(self, eid: str):
        pub = self.elsevier_request("abstract/scopus_id/" + eid.replace(self.eid_prefix, ""), "httpAccept=application%2Fjson")
        if pub == False:
            self.st.error("La richiesta per '" + eid + "' ha prodotto il seguente errore:")
            self.st.error(self.error)
            self.error = None
            return False
        if "abstracts-retrieval-response" not in pub or "authors" not in pub["abstracts-retrieval-response"]:
            self.st.error("La richiesta per '" + eid + "' non ha prodotto nessun risultato!")
            return False
        content = pub["abstracts-retrieval-response"]
        if "author" not in content["authors"]:
            self.st.error("La richiesta per '" + eid + "' non ha prodotto nessun risultato!")
            return False
        authors = content["authors"]["author"]
        pub_year = datetime.strptime(content["coredata"]["prism:coverDate"], '%Y-%m-%d').year if "coredata" in content and "prism:coverDate" in content["coredata"] else None
        puc = {"eid": eid, "pub_year": pub_year}
        for f in range(1, 3):
            puc["first" + str(f)] = None
            puc["last" + str(f)] = None
        for f in range(1, 5):
            puc["corr" + str(f)] = None
        puc["first1"] = authors[0]["@auid"]
        puc["last1"] = authors[len(authors) - 1]["@auid"]
        corr_array = []
        if "item" in content and "bibrecord" in content["item"] and "head" in content["item"]["bibrecord"] and "correspondence" in content["item"]["bibrecord"]["head"]:
            corr_el = content["item"]["bibrecord"]["head"]["correspondence"]
            if corr_el is None:
                pass
            elif type(corr_el) is dict:
                if "person" in corr_el and "ce:indexed-name" in corr_el["person"]:
                    corr_array.append(corr_el["person"]["ce:indexed-name"])
            else:
                index = 1
                for ce in corr_el:
                    if index > 5:
                        break
                    if "person" in ce and "ce:indexed-name" in ce["person"]:
                        corr_array.append(ce["person"]["ce:indexed-name"])
                    else:
                        corr_name = "" 
                        if "person" in ce:
                            for attr in ce["person"]:
                                if attr == "ce":
                                    corr_name = ce["person"][attr]
                            if corr_name != "":
                                corr_array.append(corr_name)
                    index += 1
            f = 1
            for ca in corr_array:
                for a in authors:
                    if a["ce:indexed-name"] == ca:
                        puc["corr" + str(f)] = a["@auid"]
                        f += 1
        return puc



    #-----------------------------------AUTORI
    def get_authors_for_range(self, start: int = 0):
        params = "query=af-id(60016041)"
        invs = self.elsevier_request("search/author", params, start)
        if invs == False:
            self.st.error("La richiesta per la ricerca degli autori non in anagrafica ha prodotto il seguente errore:")
            self.st.error(self.error)
            self.error = None
            return False
        if "search-results" not in invs or "entry" not in invs["search-results"]:
            self.st.error("La richiesta per la ricerca degli autori non in anagrafica non ha prodotto nessun risultato!")
            return False
        invs_total = 0 if "opensearch:totalResults" not in invs["search-results"] else int(invs["search-results"]["opensearch:totalResults"])
        invs_count = len(invs["search-results"]["entry"])
        authors = []
        for inv in invs["search-results"]["entry"]:    
            if "preferred-name" in inv and "dc:identifier" in inv:
                inv_dict = {}
                inv_dict["scopus_inv_id"] = str(inv["dc:identifier"]).replace("AUTHOR_ID:", "")
                inv_dict["inv_name"] = inv["preferred-name"]["given-name"] if "given-name" in inv["preferred-name"] else None
                inv_dict["inv_surname"] = inv["preferred-name"]["surname"] if "surname" in inv["preferred-name"] else None
                areas = []
                if "subject-area" in inv:
                    for area in inv["subject-area"]: 
                        if "@abbrev" in area and area != "@abbrev": 
                            areas.append(area["@abbrev"])
                inv_dict["inv_areas"] = areas
                names = []
                if "name-variant" in inv:
                    for name in inv["name-variant"]:   
                        full_name = ""
                        if "surname" in name:
                            full_name += str(name["surname"]) if name["surname"] is not None else ""
                        if "given-name" in name:
                            full_name += " " + str(name["given-name"]) if name["given-name"] is not None else ""
                        if full_name != "":
                            names.append(full_name)
                inv_dict["inv_names"] = names
                authors.append(inv_dict)
            else:
                pass
        return [authors, start + invs_count, invs_total]


    def get_authors(self):
        authors = []
        res = self.get_authors_for_range(0)
        if res:
            for inv in res[0]:
                authors.append(inv)
            restart = res[1] 
            total = res[2]
            while restart < total:
                res = self.get_authors_for_range(restart)
                if res:
                    for inv in res[0]:
                        authors.append(inv)
                    restart = res[1] 
                    total = res[2]   
        return authors



    #-----------------------------------CITAZIONI NON SELF O NON DEGLI AUTORI
    def get_citations(self, eid: str, author_scopus: str = None):
        params = "scopus_id=" + eid.replace(self.eid_prefix, "") + "&citation=exclude-self"
        if author_scopus:
            params += "&author_id=" + author_scopus
        pub = self.elsevier_request("abstract/citations", params)