import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import gspread as gs
import time
# from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode


st.set_page_config(page_title='Inserimento', layout = 'wide', initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- collegamento con la chiave di autenticazione per il database in firebase ---
if not firebase_admin._apps:
        cred = credentials.Certificate('firestore-key.json')
        firebase_admin.initialize_app(cred)
db = firestore.client()

#qua ho provato a collegare direttamente da google sheet

# # scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive',
# #          'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/spreadsheets']
# # creds = ServiceAccountCredentials.from_json_keyfile_name('client_secrets.json', scope)
# # client = gspread.authorize(creds)
# # link_it = "https://docs.google.com/spreadsheets/d/10DJ1wIrK7SLLt-8Sx993DeMnrJRJPeAmalrZh2Mn5Jk/edit#gid=1368264652"
# # sht = client.open_by_url(link_it)

#in alternativa ha scaricato il file excel

df = pd.read_excel("Atlas SuperSayan.xlsx").loc[:,['Nome','Cognome','Email','Area']].dropna()
for i in range(len(df)):
    nome = str(df.loc[i,'Nome']).lower().capitalize()
    cognome = str(df.loc[i,'Cognome']).lower().capitalize()
    email = str(df.loc[i,'Email']).lower()
    area = str(df.loc[i,'Area']).upper()
    db.collection('Atlas').document(email).set({'nome': nome, 'cognome':cognome , 'area':area})

col1, col2, col3, col4 = st.columns(4)
# Nome della nuova risorsa
nome = col1.text_input('Nome*')
# Cognome della nuova risorsa
cognome = col2.text_input('Cognome*')
# Email nuova risorsa
email = col3.text_input('Email*')
# Area nuova risorsa
area = col4.text_input('Area*')
# Reminder per i campi obbligatori da compilare
st.caption('\* I campi contrassegnati sono obbligatori')

if st.button('**Aggiungi risorsa**'):

    doc_ref = db.collection("Atlas").document(email)

    if email=='' or nome=='' or cognome=='' or area=='':
        st.error('Per favore, compilare tutti i campi', icon="🚨")

    else:
        nome = nome.lower().capitalize()
        cognome = cognome.lower().capitalize()
        email = email.lower()
        area = area.upper()
        doc_ref.set({'nome':nome, 
                    'cognome':cognome,
                    'area':area})
        
        st.success('Risorsa aggiunta con successo')
        time.sleep(1)
        st.experimental_rerun()

doc_ref = db.collection("Atlas")
# --- Modalità di lettura dei documenti all'interno della raccolta
docs = doc_ref.stream()

# --- Costruzione di una tabella dei dati del database
people = []
for doc in docs:
    st.write(doc)
    people_dict = {'nome': doc.to_dict()['nome'], 'cognome': doc.to_dict()['cognome'], 'email': doc.id, 'area': doc.to_dict()['area']}
    people.append(people_dict)

if people!=[]:
    data = pd.DataFrame(people)
    gd = GridOptionsBuilder.from_dataframe(data)
    gd.configure_selection(selection_mode='multiple', use_checkbox=True)
    gd.configure_grid_options(enableCellTextSelection=True)
    gd.configure_grid_options(ensureDomOrder=True)
    gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)

    gridOptions = gd.build()

    table = AgGrid(data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, height=370, fit_columns_on_grid_load=True)

    selected = table['selected_rows']

    if st.button('Elimina dalla mailing list'):
        for dict in selected:
            db.collection('Atlas').document(dict['email']).delete()

            st.success('Eliminazione effettuata')
            time.sleep(1)
            st.experimental_rerun()

else:
    st.warning('Registrazione non avvenuta')
