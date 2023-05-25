from datetime import datetime
import unicodedata

site_name = "IGG Biblio"
age_field = "FLOOR((DATE_PART('day', now() - i.date_birth) / 365)::float)"
row_height = 666


def hide_menu(st):
    hide_menu_style = """
            <style>
            header {visibility: hidden; }
            </style>
            """
    st.markdown(hide_menu_style, unsafe_allow_html=True)


def set_title(st, title=""):
    st.set_page_config(page_title = site_name if title == "" else title, layout="centered" if title == "" else "wide", page_icon=":newspaper:")
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


def strip_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFKD', text) if unicodedata.category(c) != 'Mn')


def download_excel(st, df, file_name):
    import io
    towrite = io.BytesIO()
    df.to_excel(towrite, index=False, header=True) # encoding='utf-8'
    st.download_button("Scarica in Excel", towrite, file_name + ".xlsx", "text/excel", key='download-excel')


def can_update(st, obj):
    passed_days = obj.min_days - (0 if obj.update_days == None else obj.update_days) 
    can_update = obj.update_days == None or passed_days < 1 
    if can_update:
        if obj.update_days == None:
            st.error("Nessun dato presente")
        else:
            st.success("E' possibile aggiornare i dati")
    else:
        st.warning("E' possibile aggiornare i dati tra " + str(passed_days) + " giorni")
    return can_update


all_years = "Intera carriera"
def select_year(st, all: bool = False, label: str = "Anno selezionato:"):
    years = [datetime.now().year, datetime.now().year - 1]
    if all:
        years[0:0] = [all_years]
    return st.selectbox('Anno selezionato:', years)


def set_prop(st, label: str, value: any):
    st.write(label + ": **" + (str(value) if value == 0 or value else "Non disponibile") + "**")


def calculate_email(author):
    author_email = ""
    author_array = str(author).lower().split(" ")
    if len(author_array) > 2:
        if len(author_array[0]) > 3:
            author_email = author_array[1] + author_array[0]
        else:
            author_email = author_array[2] + author_array[0] + author_array[1]
    elif len(author_array) > 1:
        author_email = author_array[1] + author_array[0]
    else:
        author_email = author_array[0]
    author_email += "@gaslini.org"
    author_email = strip_accents(author_email)
    return author_email