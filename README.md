# Instructions
## Prerequisites 
Inside your project folder you need to launch the following instructions:

```
pip3 install pipenv
pipenv shell

pipenv install streamlit
pipenv install psycopg2-binary
```
Create the file **.streamlit/secrets.toml** with the following valued fields:
```
db_host = ""
db_name = ""
db_username = ""
db_password = ""
```
In the end you can launch the server from the project folder:
```
pipenv shell
streamlit run 0_Home.py
```
