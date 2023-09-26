import requests
import json

class Scival_import:
    st = None
    year = 0
    max_reqs = 20
    author_count = 0
    proxies = {
    'http': 'http://fg-proxy-c.gaslini.lan:8080',
    'https': 'http://fg-proxy-c.gaslini.lan:8080',
    }
    error = None


    def __init__(self, st):
        self.st = st


    def get_hindex(self, authors):
        params = ""
        params += "metricTypes=HIndices"
        params += "&authors=" + authors
        params += "&yearRange=10yrs"
        params += "&includeSelfCitations=false"
        params += "&byYear=false"
        params += "&includedDocs=AllPublicationTypes"
        params += "&journalImpactType=CiteScore"
        params += "&showAsFieldWeighted=false"
        params += "&indexType=hIndex"
        params += "&apiKey=7f59af901d2d86f78a1fd60c1bf9426a" #self.st.secrets["scopus_key"]
        #self.st.success(authors)
        #return False
        return self.scival_request("author/metrics", params)


    def scival_request(self, function, params):
        url = 'https://api.elsevier.com/analytics/scival/' + function + '?' + params
        try:
            response = requests.get(url, verify = True, proxies = self.proxies, timeout = 5)
            return json.loads(response.content)
        except requests.exceptions.RequestException as e: 
            self.error = e
            return False 