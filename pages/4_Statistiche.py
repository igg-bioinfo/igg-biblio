import streamlit as st
from utils import set_title, select_year
from classes.db_psql import *
from classes.user import *
from classes.statistics import *

title = "Statistiche"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

year = select_year(st)
stats = Statistics(st, db, year)
stats.get_stats_units(0)
stats.get_stats_units(40)
unit = stats.select_units()
stats.get_invs_by_unit(unit)

db.close()