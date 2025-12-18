import streamlit as st
import pandas as pd
from services.api_client import APIClient

def render_dashboard(api_client: APIClient):
    token = st.session_state.token
    username = st.session_state.username
    
    st.title(f"📊 Dashboard Gerencial")
    st.markdown(f"Bienvenido, **{username}**")
    
    # --- Data Fetching ---
    summary = api_client.get_sales_summary(token)
    hourly_data = api_client.get_hourly_sales(token)
    low_stock = api_client.get_low_stock_products(token)
    
    # --- KPIs ---
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ventas Hoy", f"${summary['daily_sales']:,.2f}")
        
    with col2:
        st.metric("Transacciones", summary['transactions'])
        
    with col3:
        st.metric("Margen Promedio", f"{summary['avg_margin']}%")
        
    st.divider()
    
    # --- Charts ---
    st.subheader("Ventas por Hora")
    chart_data = pd.DataFrame({
        "Hora": hourly_data['hours'],
        "Ventas": hourly_data['sales']
    })
    st.bar_chart(chart_data.set_index("Hora"))
    
    st.divider()
    
    # --- Low Stock Alert ---
    st.subheader("⚠️ Alerta de Stock Bajo")
    if low_stock:
        df_stock = pd.DataFrame(low_stock)
        st.warning(f"Se detectaron {len(low_stock)} productos con stock crítico.")
        st.dataframe(
            df_stock,
            column_config={
                "id": "ID",
                "name": "Producto",
                "stock": "Stock Actual",
                "min_stock": "Mínimo" # Fixed encoding
            },
            use_container_width=True,
            hide_index=True
        )
    else:
        st.success("Todo el inventario está en niveles óptimos.")
