import streamlit as st
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import time
import pandas as pd
from trycourier import Courier
import email_validator

st.set_page_config(page_title='Mail ✉️', layout = 'wide', initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

st.title("Invio Mail")

# --- collegamento con la chiave di autenticazione per il database in firebase ---
if not firebase_admin._apps:
        cred = credentials.Certificate('firestore-key.json')
        firebase_admin.initialize_app(cred)
db = firestore.client()

def validazione_email(email):
    try:
        email_validator.validate_email(email)
        return True
    except email_validator.EmailNotValidError:
        return False

choice = st.radio('Scegli a chi inviare la mail ', ['Persona singola', 'Gruppo di persone'])

if choice == 'Persona singola':
    mail_destinatario = st.text_input("Inserisci la mail del destinatario: ")
    oggetto = st.text_input("Inserisci l'oggetto della mail: ")
    body = st.text_area("Inserisci il contenuto della mail: ")
    invio = st.button("Invia mail")
    
    if invio:
        if body == '':
            st.warning('⚠️ Inserisci un contenuto valido per il corpo della mail')
        elif mail_destinatario == '':
            st.warning('⚠️ Inserisci una mail valida per il destinatario')
        elif not validazione_email(mail_destinatario): 
            st.warning('⚠️ Formato email del destinatario non valido')
        else:
            # Dividi l'indirizzo email sulla base dell'@ e del punto
            parts = mail_destinatario.split('@')[0].split('.')

            # Estrai il nome e il cognome dalla lista 'parts'
            nome_dest = parts[0]
            cognome_dest = parts[1]
            
            client = Courier(auth_token="pk_prod_1GFDJ6KZ5Q4N9GQZ59Y1C197WSXX")

            resp = client.send_message(
            message={
                "to": {
                "email": mail_destinatario, 
                },
                "data": {
                "name": nome_dest + ' ' + cognome_dest,
                },
                "content": {
                "title": oggetto,
                "body": body,
                },
                "routing": {
                "method": "single",
                "channels": ["email"],
                },
            }
            )

            st.success('Email inviata con successo!')
        time.sleep(1)
        st.experimental_rerun()
        
        
if choice == 'Gruppo di persone':
    docs = db.collection(u'Gruppi').stream()
    nomi = ['']
    for doc in docs:
        nomi.append(doc.to_dict()['name'])

    gruppo = st.selectbox('Seleziona il gruppo a cui vuoi inviare una mail', nomi)
    oggetto = st.text_input("Inserisci l'oggetto della mail: ")
    body = st.text_area("Inserisci il contenuto della mail: ")
    invio = st.button("Invia mail")

    if gruppo != '':
        # --- Modalità di lettura di una specifica raccolta all'interno del database
        doc_ref = db.collection(u'Gruppi')
        # --- Modalità di lettura dei documenti all'interno della raccolta
        docs = doc_ref.stream()
        # --- Costruzione di una tabella dei dati del database
        listass = []
        for doc in docs:
            if doc.to_dict()['name'] == gruppo:
                listass_dict = {'maillist': doc.to_dict()['maillist']}
                listass.append(listass_dict)

    if invio:
        if body == '':
            st.warning('⚠️ Inserisci un contenuto valido per il corpo della mail')
        elif gruppo == '':
            st.warning('⚠️ Inserisci un gruppo valido')
        else:
            
            #TRYCOURIER
            for i in doc.to_dict()['maillist']:
                stringa_nominativo=i.lower()
                
                nome, cognome = stringa_nominativo.split( )
                mail = nome + '.' + cognome + '@jesap.it'
                
                client = Courier(auth_token="pk_prod_1GFDJ6KZ5Q4N9GQZ59Y1C197WSXX")

                resp = client.send_message(
                message={
                    "to": {
                    "email": mail, 
                    },
                    "data": {
                    "name": i,
                    },
                    "content": {
                    "title": oggetto,
                    "body": body,
                    },
                    "routing": {
                    "method": "single",
                    "channels": ["email"],
                    },
                }
                )

                st.success('Email inviata con successo!')
        time.sleep(1)
        st.experimental_rerun()
