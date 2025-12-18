import streamlit as st
import pandas as pd
from services.api_client import APIClient

def render_inventory_view(api_client: APIClient):
    st.title("📦 Inventario")
    
    token = st.session_state.token
    
    # --- Fetch Data (Cached hopefully in future, now direct fetch) ---
    with st.spinner("Actualizando catálogo..."):
        products = api_client.get_products(token)
        
    if not products:
        st.warning("No se pudieron cargar los productos.")
        return
        
    # --- Search ---
    search_term = st.text_input("🔍 Buscar producto (Nombre o Código)", "")
    
    # --- Filter Logic ---
    df = pd.DataFrame(products)
    
    if search_term:
        # Case insensitive search
        mask = df.apply(lambda x: search_term.lower() in str(x['name']).lower() or search_term.lower() in str(x.get('code','')).lower(), axis=1)
        df_filtered = df[mask]
    else:
        df_filtered = df
        
    # --- Display ---
    st.caption(f"Mostrando {len(df_filtered)} productos")
    
    # Select columns to show
    cols_to_show = ["name", "price", "stock", "category_id"] 
    # Rename for display
    df_display = df_filtered[cols_to_show].copy()
    df_display.columns = ["Producto", "Precio ($)", "Stock", "Categoría"]
    
    # Highlight low stock
    st.dataframe(
        df_display,
        column_config={
            "Precio ($)": st.column_config.NumberColumn(format="$%.2f"),
            "Stock": st.column_config.NumberColumn(help="Cantidad disponible"),
        },
        use_container_width=True,
        hide_index=True
    )
