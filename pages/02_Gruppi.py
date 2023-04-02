import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
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


col1, col2= st.columns(2)

associati = db.collection(u'Atlas').get()

nomi_ass = [f"{u.get('nome')} {u.get('cognome')}" for u in associati]

listass = col1.multiselect("Scegli gli associati che vuoi inserire nel gruppo", nomi_ass)

group_name = col2.text_input("Inserisci il nome del gruppo:")

if st.button("Aggiungi gruppo"):

        db.collection(u'Groups').add({
                u'maillist': listass,
                u'name': group_name
        })

        st.success("Il Gruppo è stato aggiunto con successo!")
