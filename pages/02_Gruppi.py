import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
import pandas as pd
from st_aggrid import GridOptionsBuilder, AgGrid, GridUpdateMode


st.set_page_config(page_title='Gruppi', layout = 'wide', initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Gruppi")
# --- collegamento con la chiave di autenticazione per il database in firebase ---
if not firebase_admin._apps:
        cred = credentials.Certificate('firestore-key.json')
        firebase_admin.initialize_app(cred)
db = firestore.client()


col1, col2= st.columns(2)

associati = db.collection(u'Atlas').get()

nomi_ass = [f"{u.get('nome')} {u.get('cognome')}" for u in associati]

listass = col1.multiselect("Scegli gli associati che vuoi inserire nel gruppo", nomi_ass)

group_name = col2.text_input("Inserisci il nome del gruppo:")

if st.button("Aggiungi gruppo"):
        
        if group_name == '':
                st.warning('⚠️ Inserisci un nome valido al grouppo')
        if len(listass)<2:
                st.warning('⚠️ Inserisci almeno due nomi dalla lista per creare un gruppo')

        db.collection(u'Gruppi').document("grupppo_"+group_name).set({
                u'maillist': listass,
                u'name': group_name
        })

        st.success("Il Gruppo è stato aggiunto con successo!")
# --- Modalità di lettura di una specifica raccolta all'interno del database
doc_ref = db.collection(u"Gruppi")
# --- Modalità di lettura dei documenti all'interno della raccolta
docs = doc_ref.stream()

# --- Costruzione di una tabella dei dati del database
people = []
for doc in docs:
        #st.write(doc)
        people_dict = {'mail list': doc.to_dict()['maillist'], 'name': doc.to_dict()['name']}
        people.append(people_dict)

if people!=[]:
        data = pd.DataFrame(people)
        gd = GridOptionsBuilder.from_dataframe(data)
        gd.configure_selection(selection_mode='multiple', use_checkbox=True)
        gd.configure_grid_options(enableCellTextSelection=True)
        gd.configure_grid_options(ensureDomOrder=True)
        gd.configure_pagination(enabled=True, paginationAutoPageSize=False, paginationPageSize=6)

        gridOptions = gd.build()

        table = AgGrid(data, gridOptions=gridOptions, update_mode=GridUpdateMode.SELECTION_CHANGED, enable_enterprise_modules=False, height=270, fit_columns_on_grid_load=True)

        selected = table['selected_rows']



        if st.button('Elimina gruppi selezionati'):
                for dict in selected:
                        db.collection(u'Gruppi').document(dict['gruppo_'+dict['name']]).delete()

                        st.success('Eliminazione effettuata')
                        time.sleep(1)
                        st.experimental_rerun()

else:
        st.warning('Nessun gruppo registrato')
