import streamlit as st
from services.api_client import APIClient
from views.login_view import render_login
from views.dashboard_view import render_dashboard

from views.sales_view import render_sales_view
from views.inventory_view import render_inventory_view

# --- Config ---
st.set_page_config(
    page_title="ERP Dashboard",
    page_icon="📊",
    layout="wide"
)

# --- Session State Init ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.current_view = "Dashboard"

# --- Main App Logic ---
def main():
    api_client = APIClient()

    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2920/2920349.png", width=100) # Placeholder Icon
        st.markdown("### Ferretería ERP")
        
        if st.session_state.logged_in:
            st.markdown("---")
            # Navigation Menu
            view = st.radio("Navegación", ["Dashboard", "Ventas", "Inventario"], label_visibility="collapsed")
            st.session_state.current_view = view
            
            st.markdown("---")
            if st.button("Cerrar Sesión", type="primary"):
                st.session_state.logged_in = False
                st.session_state.token = None
                st.session_state.username = None
                st.rerun()

    # Content
    if not st.session_state.logged_in:
        render_login(api_client)
    else:
        if st.session_state.current_view == "Dashboard":
            render_dashboard(api_client)
        elif st.session_state.current_view == "Ventas":
            render_sales_view(api_client)
        elif st.session_state.current_view == "Inventario":
            render_inventory_view(api_client)

if __name__ == "__main__":
    main()
