import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.user_request import *

title = "Richieste per l'inserimento di un nuovo ricercatore"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

requests = User_request(st, db)
requests.show_pendings()