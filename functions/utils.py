site_name = "IGG Biblio"

def hide_menu(st):
    hide_menu_style = """
            <style>
            #MainMenu {visibility: hidden; }
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def set_title(st, title=""):
    st.set_page_config(page_title = site_name if title == "" else title, layout="centered" if title == "" else "wide")
    if title != "":
        title = " - " + title
    st.title(site_name + title)
    #hide_menu(st)

