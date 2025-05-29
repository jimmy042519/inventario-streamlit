import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ===== CONFIGURACIÓN INICIAL =====
st.set_page_config(page_title="Sistema de Inventario", page_icon="📦")

# ===== FUNCIONES CORE =====
@st.cache_data
def cargar_datos():
    """Carga datos desde Excel o crea DataFrame vacío"""
    if os.path.exists("inventario.xlsx"):
        df = pd.read_excel("inventario.xlsx")
        # Convertir columnas necesarias
        if 'Última Actualización' not in df.columns:
            df['Última Actualización'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return df
    return pd.DataFrame(columns=["ID", "Producto", "Cantidad", "Categoría", "Última Actualización"])

def guardar_datos(df):
    """Guarda los datos en Excel"""
    df.to_excel("inventario.xlsx", index=False)

@st.cache_data
def buscar_producto(termino, df):
    """Búsqueda en múltiples columnas"""
    termino = str(termino).lower()
    return df[
        df['Producto'].str.lower().str.contains(termino) |
        df['ID'].astype(str).str.contains(termino) |
        df['Categoría'].str.lower().str.contains(termino)
    ]

# ===== VISTAS/PÁGINAS =====
def mostrar_inventario(df):
    st.title("📦 Inventario Actual")
    st.dataframe(df.sort_values(by="Última Actualización", ascending=False))

def añadir_producto(df):
    st.title("➕ Añadir Producto")
    
    with st.form("formulario_producto"):
        col1, col2 = st.columns(2)
        with col1:
            producto = st.text_input("Nombre del producto*")
        with col2:
            cantidad = st.number_input("Cantidad*", min_value=1, step=1)
        
        categoria = st.selectbox("Categoría", ["Electrónica", "Ropa", "Alimentos", "Otros"])
        
        if st.form_submit_button("Guardar"):
            if not producto:
                st.error("El nombre es obligatorio")
                return
                
            nuevo_id = f"PROD-{len(df)+1:03d}"
            nuevo_registro = pd.DataFrame([{
                "ID": nuevo_id,
                "Producto": producto,
                "Cantidad": cantidad,
                "Categoría": categoria,
                "Última Actualización": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            df = pd.concat([df, nuevo_registro], ignore_index=True)
            guardar_datos(df)
            st.success(f"Producto {nuevo_id} añadido")
            st.balloons()
            st.experimental_rerun()

def buscar_productos(df):
    st.title("🔍 Buscar Productos")
    termino = st.text_input("Ingrese término de búsqueda")
    
    if termino:
        resultados = buscar_producto(termino, df)
        if not resultados.empty:
            st.success(f"Resultados ({len(resultados)}):")
            st.dataframe(resultados)
        else:
            st.warning("No se encontraron coincidencias")

# ===== MAIN =====
def main():
    df = cargar_datos()
    
    # Sidebar (navegación)
    with st.sidebar:
        st.title("Menú")
        opcion = st.radio("Seleccione acción:", 
                         ["Ver Inventario", "Añadir Producto", "Buscar Productos"])
        
        st.divider()
        st.info(f"Total productos: {len(df)}")
    
    # Router de páginas
    if opcion == "Ver Inventario":
        mostrar_inventario(df)
    elif opcion == "Añadir Producto":
        añadir_producto(df)
    elif opcion == "Buscar Productos":
        buscar_productos(df)

if __name__ == "__main__":
    main()