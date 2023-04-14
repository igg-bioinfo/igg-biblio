import streamlit as st
import pandas as pd
import numpy as np
import time
from login import *

st.set_page_config(page_title="Plotting Demo", page_icon="📈")

is_logged = False

hide_menu_style = """
        <style>
        --#MainMenu {visibility: hidden; }
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

    
if check_password(st):
    st.write("Here goes your normal Streamlit app...")
    st.button("Click me")


#   streamlit run main.py --server.port 8089
df = pd.DataFrame(
   np.random.randn(50, 20),
   columns=('col %d' % i for i in range(20)))


st.dataframe(df) 
csv = df.to_csv().encode('utf-8')
st.download_button(
    label="Download data as CSV",
    data=csv,
    file_name='large_df.csv',
    mime='text/csv',
)
st.write("prova")
st.write("DB username:", st.secrets["db_username"])
st.write("DB password:", st.secrets["db_password"])
st.write("My cool secrets:", st.secrets["my_cool_secrets"]["things_i_like"])

if is_logged == False:
    with st.form("my_form"):
        st.write("Login")
        input_usr = st.slider("Form slider")
        imput_pw = st.checkbox("Form checkbox")

        # Every form must have a submit button.
        submitted = st.form_submit_button("Submit")
        if submitted:
            with st.spinner('Wait for it...'):
                time.sleep(5)
                st.success('Done!')
                is_logged = True
            #st.write("slider", slider_val, "checkbox", checkbox_val)

with st.sidebar:
    st.title("IGG Biblio")
    if st.button('Say hello'):
        st.write('Why hello there')
st.stop()
st.write("not stop")