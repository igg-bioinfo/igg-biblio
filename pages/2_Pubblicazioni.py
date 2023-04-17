import streamlit as st
from functions.utils import *
from classes.db_psql import *
from classes.user import *

title = "Pubblicazioni"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()