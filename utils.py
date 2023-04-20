site_name = "IGG Biblio"

def hide_menu(st):
    hide_menu_style = """
            <style>
            header {visibility: hidden; }
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)

def set_title(st, title=""):
    st.set_page_config(page_title = site_name if title == "" else title, layout="centered" if title == "" else "wide")
    if title == "":
        title = site_name
    st.title(title)
    #hide_menu(st)
    
def get_month(month):
    month_int = month
    if month == 'Jan':
        month_int = '01'
    if month == 'Feb':
        month_int = '02'
    if month == 'Mar':
        month_int = '03'
    if month == 'Apr':
        month_int = '04'
    if month == 'May':
        month_int = '05'
    if month == 'Jun':
        month_int = '06'
    if month == 'Jul':
        month_int = '07'
    if month == 'Aug':
        month_int = '08'
    if month == 'Sep':
        month_int = '09'
    if month == 'Oct':
        month_int = '10'
    if month == 'Nov':
        month_int = '11'
    if month == 'Dec':
        month_int = '12'
    return month_int

def download_excel(st, df, file_name):
    import io
    towrite = io.BytesIO()
    df.to_excel(towrite, encoding='utf-8', index=False, header=True)
    st.download_button("Scarica in Excel", towrite, file_name + ".xlsx", "text/excel", key='download-excel')

def set_msg_for_update(st, obj):
    if obj.update_days != None:
        st.success("E' possibile aggiornare i dati")