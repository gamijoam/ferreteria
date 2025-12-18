import streamlit as st
import pandas as pd
import datetime
from services.api_client import APIClient

def render_sales_view(api_client: APIClient):
    st.title("💰 Historial de Ventas")
    
    token = st.session_state.token
    
    # --- Filters ---
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Desde", datetime.date.today())
    with col2:
        end_date = st.date_input("Hasta", datetime.date.today())
        
    if start_date > end_date:
        st.error("La fecha 'Desde' no puede ser mayor a 'Hasta'")
        return

    # --- Fetch Data ---
    with st.spinner("Cargando ventas..."):
        sales_data = api_client.get_detailed_sales(token, start_date, end_date)
    
    if not sales_data:
        st.info("No hay ventas registradas en este período.")
        return
        
    # --- Process Data ---
    data = []
    total_periodo = 0
    total_items = 0
    
    for sale in sales_data:
        # La API devuelve objetos Sale, adaptamos a tabla plana
        total_periodo += sale.get('total_amount', 0)
        
        # Calculate items count (if details present)
        items_count = len(sale.get('details', []))
        total_items += items_count

        data.append({
            "ID": sale.get('id'),
            "Fecha": sale.get('date', '').split('T')[0],
            "Cliente": sale.get('customer_id', 'Genérico'), # A futuro: mapear nombre cliente
            "Método Pago": sale.get('payment_method', 'N/A'),
            "Total ($)": sale.get('total_amount'),
            "Items": items_count
        })
    
    df = pd.DataFrame(data)
    
    # --- Summary Metrics ---
    m1, m2, m3 = st.columns(3)
    m1.metric("Total Vendido", f"${total_periodo:,.2f}")
    m2.metric("Transacciones", len(sales_data))
    m3.metric("Productos Vendidos", total_items)
    
    st.divider()
    
    # --- Table ---
    st.dataframe(
        df,
        column_config={
            "Total ($)": st.column_config.NumberColumn(format="$%.2f"),
        },
        use_container_width=True,
        hide_index=True
    )
