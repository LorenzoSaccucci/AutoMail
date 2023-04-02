import streamlit as st

st.set_page_config(page_title='Inserimento', layout = 'wide', initial_sidebar_state = 'auto')
hide_streamlit_style = """
            <style>
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)


st.write("HOME")