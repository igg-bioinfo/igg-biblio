# LibRA – Library for Research Assessment

This system consists of **two web applications** designed to manage bibliometric data for researchers.
This is a web application to manage pubblication from PubMed, Scopus and Journal Citation Reports.

---

## Installation
You can use 2 different method to run this web application:

### pipenv
Inside your project folder you can launch the following instructions:
```
pip3 install pipenv
pipenv shell

pipenv install streamlit
pipenv install psycopg2-binary
pipenv install openpyxl
```

### mamba / conda
Create an environment with python 3.10:
```
mamba create --name streamlit python=3.10
```
Activate the environment and inside install the required libraries:
```
mamba activate streamlit
mamba install pip
pip install streamlit
mamba install psycopg2-binary
mamba install openpyxl
```
Or from enviroment.yml:
```
mamba env create -f environment.yml
mamba activate streamlit
```

### Config Files 
Create the file **.streamlit/config.toml** in your project folder with the following valued fields:
```
[server]
port = ""

[browser]
serverAddress = ""

[theme]
backgroundColor = "#fff"
```
Create the file **.streamlit/secrets.toml** in your project folder with the following valued fields:
```
db_host = ""
db_name = ""
db_username = ""
db_password = ""
scopus_key = ""
```
In the end you can launch the server from the project folder inside the conda or pipenv environment:
```
streamlit run 0_Home.py
```

---

## The database structure

The PostgreSQL database is composed by the following tables:
investigator_details
investigator_requests
investigators
pubmed_pubs
scopus_failed
scopus_invs
scopus_metrics
scopus_pubs_all
scopus_pucs
users

---

## 🧾 Summary

### 1. **Admin Web Application**

A web interface for administrators and bibliometric officers. It provides full control over researcher records, publication imports from Scopus and PubMed, metric calculations (e.g., h-index), and the handling of external data requests.  
It includes dashboards for statistics, validation of publication data, and demographic management.

### 2. **Researcher Web Application**

A simplified portal for individual researchers. After logging in, each researcher can update their own demographic information and view their publications and metrics. A public request form is also available for individuals not yet listed to apply for inclusion in the system.

---

# 📊 Admin Web Application

The admin web application is composed of 8 main sections:

- **Homepage**  
- **Demographic Data (Anagrafica)**  
- **Researcher Details (Dati dei Ricercatori)**  
- **Albo**  
- **Statistics (Statistiche)**  
- **Requests (Richieste)**  
- **Scopus**  
- **PubMed**  

---

### 🏠 Homepage

The homepage acts as the control center for launching all import operations. It is divided into several functional blocks:

- **Anagrafica** – Manage and import researcher demographic data.  
- **Albo** – Update publication and metric data via Scopus.  
- **PUC from Scopus** – Retrieve *First, Last, Corresponding* authorship roles.  
- **PubMed – Publications** – Import publication data from PubMed.

---

### 👥 Anagrafica

Allows the import of researcher demographic data (e.g., name, surname, department, Scopus ID, PubMed ID, etc.) via Excel file upload for a selected year.

---

### 📚 Albo

After importing researchers, this section allows importing all related publications from the **Scopus API (Elsevier)** using an API key configured in `config.toml`.

For each publication, the following metrics are calculated:

- **h-index**
- **Number of publications**
- **Total citations**

These metrics are computed over three time frames:

- Entire career  
- Last 10 years  
- Last 5 years

---

### ✍️ PUC from Scopus

This section allows the retrieval of **First**, **Last**, and **Corresponding** authors (FLC) for each publication imported from Scopus. The roles are cross-referenced with the existing demographic data.

---

### 🧾 PubMed – Publications

Allows retrieval of all publications available on **PubMed** for each listed researcher using the **PubMed API**.

---

## 📄 Demographic Data (Anagrafica)

Displays a table of all researchers for a selected year. The data can be sorted, filtered, or exported to Excel.

---

## 👤 Researcher Details (Dati dei Ricercatori)

Allows selection of individual researchers to view:

- All associated metrics
- PubMed publications not yet listed in Scopus

Also enables updates to researcher demographic details if the imported data was incorrect or outdated.

---

## 🗂️ Albo

Displays a table of all researchers sorted by **h-index**. Each row summarizes the main bibliometric indicators for each individual.

---

## 📈 Statistics

This section provides three key views:

1. **Metrics summary by organizational unit** – includes median h-index, number of members, etc.  
2. **Metrics for members under 40** – filtered by age.  
3. **Individual metrics** – for each member in a selected unit.

---

## 📥 Requests (Richieste)

Interface for managing external user requests to be added to the researcher list. Requests can be **accepted** or **rejected** by an admin.

---

## 🔍 Scopus

Displays all publications retrieved from the **Scopus API**, organized by year and by researcher.

Also includes a secondary table listing **PubMed publications not found in Scopus**, to help identify gaps and ensure data completeness.

---

## 🔎 PubMed

Displays all publications retrieved from the **PubMed API**, organized by year and by researcher, based on the demographic records.

---

# 👨‍🔬 Researcher Web Application

The researcher portal includes two main pages:

### 1. **Researcher Dashboard (with login)**

After logging in, researchers can:

- View their publications and bibliometric metrics
- Update their demographic data, including:
  - Email
  - Name, surname
  - Contract type
  - Unit/department
  - Scopus ID, ORCID, Researcher ID

### 2. **Public Request Form (no login)**

A public-facing page that allows individuals **not yet listed** in the researcher database to request inclusion.  
They must provide all necessary demographic information to be reviewed by the admin team.