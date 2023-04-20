# About
This is a web application to manage pubblication from PubMed, Scopus and Journal Citation Reports.

# Instructions
You can use 2 different method to run this web application:

## pipenv
Inside your project folder you can launch the following instructions:
```
pip3 install pipenv
pipenv shell

pipenv install streamlit
pipenv install psycopg2-binary
pipenv install openpyxl
```

## mamba / conda
Create an environment with python 3.10:
```
mamba create --name streamlit python=3.10
```
Activate the environment and inside install the required libraries:
```
conda activate streamlit
pip install streamlit
mamba install psycopg2-binary
mamba install openpyxl
```

## Config Files 
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
