import streamlit as st
from services.api_client import APIClient

def render_login(api_client: APIClient):
    st.title("🔒 Acceso al ERP")
    
    with st.form("login_form"):
        username = st.text_input("Usuario")
        password = st.text_input("Contraseña", type="password")
        
        submit = st.form_submit_button("Ingresar")
        
        if submit:
            if not username or not password:
                st.error("Por favor ingrese usuario y contraseña")
            else:
                with st.spinner("Autenticando..."):
                    token = api_client.login(username, password)
                    
                if token:
                    st.session_state.logged_in = True
                    st.session_state.token = token
                    st.session_state.username = username
                    st.success("Login exitoso!")
                    st.rerun()
                else:
                    st.error("Credenciales inválidas o error de conexión con API")
