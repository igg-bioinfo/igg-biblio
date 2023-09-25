import requests
import xml.etree.ElementTree as et
from utils import get_month

class Pubmed_import:
    st = None
    year = 0
    max_pubs = 300
    pub_count = 0
    proxies = {
    'http': 'http://fg-proxy-c.gaslini.lan:8080',
    'https': 'http://fg-proxy-c.gaslini.lan:8080',
    }
    error = None


    def __init__(self, st, year):
        self.st = st
        self.year = year
    

    def is_error(self):
        return self.error != None


    def entrez_request(self, function, params):
        url = 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/' + function + '.fcgi?' + params
        try:
            response = requests.get(url, verify = True, proxies = self.proxies, timeout = 5)
            return et.fromstring(response.content)
        except requests.exceptions.RequestException as e: 
            self.error = e
            return False 
        

    def get_date(self, date):
        dt = ''
        if date:
            if date.find('Year') != None:
                dt += date.find('Year').text
            if date.find('Month') != None:
                dt += '-' + get_month(date.find('Month').text)
            if date.find('Day') != None:
                dt += '-' + date.find('Day').text
        return dt
    

    def group_ids(self, xml, ids_field):
        grouped_ids = []
        if xml:
            ids = ''
            index = 0
            for id in xml.find(ids_field):
                ids += id.text + ' '
                if index < self.max_pubs:
                    index += 1
                else: 
                    grouped_ids.append(ids)
                    ids = ''
                    index = 0
            if ids != '':
                grouped_ids.append(ids)
        return grouped_ids
    

    def get_pubblication(self, xml):
        pmid = xml.find('MedlineCitation/PMID').text
        issn = xml.find('MedlineCitation/MedlineJournalInfo/ISSNLinking').text if xml.find('MedlineCitation/MedlineJournalInfo/ISSNLinking') != None else '' 
        doi = None
        for eloc_id in xml.findall('MedlineCitation/Article/ELocationID'):
            if eloc_id.get('EIdType') == 'doi':
                doi = eloc_id.text
                break
        if doi == None:
            for art_id in xml.findall('PubmedData/ArticleIdList/ArticleId'):
                if art_id.get('IdType') == 'doi':
                    doi = art_id.text
                    break

        journal = xml.find('MedlineCitation/Article/Journal/Title').text
        title = xml.find('MedlineCitation/Article/ArticleTitle').text
        if title == None:
            #regex su <ArticleTitle>*</ArticleTitle>
            pass
        pdate = self.get_date(xml.find('MedlineCitation/Article/Journal/JournalIssue/PubDate'))
        if pdate == '':
            pdate = self.get_date(xml.find('MedlineCitation/Article/ArticleDate'))
        pmcid = None
        for art_id in xml.findall('PubmedData/ArticleIdList/ArticleId'):
            if art_id.get('IdType') == 'pmc':
                pmcid = art_id.text.replace('PMC', '')
                break
        self.pub_count += 1

        return {"pm_id": pmid, "doi": doi, "journal": journal, "issn": issn, "title": title, "pub_date": pdate, "pmc_id": pmcid }


    def get_authors(self, xml):
        first = True
        author_list = xml.find('MedlineCitation/Article/AuthorList')
        a_count = len(author_list)
        index = 0
        a_pos_prev = ''
        authors = []
        for a in author_list:
            
            author_orcid = a.find('Identifier').text.replace('http://orcid.org/', '').replace('https://orcid.org/', '') if a.find('Identifier') != None else ''
            
            author = ''
            author += a.find('LastName').text if a.find('LastName') != None else '' 
            author += ' ' + a.find('ForeName').text if a.find('ForeName') != None else ''
            group = ' ' + a.find('CollectiveName').text if a.find('CollectiveName') != None else ''
                
            a_pos = 'NA'
            index += 1
            co_author = 'EqualContrib' in a.attrib
            if author != '' or group != '':
                if co_author:
                    a_pos = 'Co-' + ('last' if index == a_count else ('first' if first or a_pos_prev == 'Co-first' else 'last'))
                    first = False
                elif first:
                    a_pos = 'First'
                    first = False
                elif index == a_count:
                    a_pos = 'Last'
                else:
                    a_pos = 'Intermediate' 
                a_pos_prev = a_pos
            
            affiliations = []
            affiliations_txt = ""
            for aff in a.findall('AffiliationInfo'):
                affiliations.append(aff.find('Affiliation').text)
                affiliations_txt += aff.find('Affiliation').text + ' '

            #la @ per controllare che ci sia una email e affiliazione gaslini
            corresponding = affiliations_txt.find('@') != -1 and affiliations_txt.lower().find('gaslini') != -1

            author_dict = {}
            author_dict["author_orcid"] = author_orcid
            author_dict["author_name"] = group if author == '' else author
            author_dict["is_person"] = author != ''
            author_dict["position"] = a_pos
            author_dict["corresponding"] = corresponding
            author_dict["affiliations"] = affiliations
            authors.append(author_dict)
        return authors


    def get_pubs(self):
        pubs = []
        self.pub_count = 0
        xml_ids = self.entrez_request('esearch', 'db=pubmed&term=*gaslini*[ad]' + str(self.year) + '[dp]&retmax=99999')
        if self.is_error():
            return pubs
        grouped_ids = self.group_ids(xml_ids, 'IdList')
        if grouped_ids == None:
            self.st.error("Nessun id trovato")
            return pubs
        for ids in grouped_ids:
            xml_pubs = self.entrez_request('efetch', 'db=pubmed&id=' + ids + '&retmode=xml')
            if xml_pubs:
                for xml_pub in xml_pubs:
                    pub_dict = self.get_pubblication(xml_pub)
                    pub_dict['authors'] = self.get_authors(xml_pub)
                    pubs.append(pub_dict)
        return pubs