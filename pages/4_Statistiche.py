import streamlit as st
from utils import *
from classes.db_psql import *
from classes.user import *
from classes.statistics import *

title = "Statistiche"
set_title(st, title)

db = DB(st)
db.connect()
user = User(st, db)
user.is_logged()

year = select_year(st, db, 'scopus_pubs_all')
stats = Statistics(st, db, year)
stats.get_stats_units(0)

st.markdown("---")
stats.get_stats_units(40)

st.markdown("---")
st.markdown("### Membri delle unità")
unit = stats.select_units()
stats.get_invs_by_unit(unit)

db.close()