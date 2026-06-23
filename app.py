import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(
    page_title="CHICANEROS - Registro de Ventas",
    page_icon="🍗",
    layout="wide"
)

MENU = {
    "Combo Ego (Tenders x2)":     {"categoria": "Combo",          "precio": 20000},
    "Combo Petalo (Tenders x4)":  {"categoria": "Combo",          "precio": 30000},
    "Combo Panas (Tenders x8)":   {"categoria": "Combo",          "precio": 55000},
    "Combo Family (Tenders x12)": {"categoria": "Combo",          "precio": 80000},
    "Drinks (Coca-Cola)":         {"categoria": "Bebida",         "precio": 6000},
    "Tender Dog":                 {"categoria": "Especialidad",   "precio": 15000},
    "Chickn Fries Personal":      {"categoria": "Especialidad",   "precio": 25000},
    "Chickn Fries Grande":        {"categoria": "Especialidad",   "precio": 35000},
    "Tenders x2":                 {"categoria": "Individual",     "precio": 12000},
    "Vaso de Salsa":              {"categoria": "Adicional",      "precio": 6500},
    "Fries":                      {"categoria": "Acompanamiento", "precio": 7000},
}

CSV_PATH = "ventas.csv"

def cargar_ventas():
    if os.path.exists(CSV_PATH):
        return pd.read_csv(CSV_PATH)
    return pd.DataFrame(columns=[
        "Fecha", "Hora", "Producto", "Categoria",
        "Cantidad", "Precio Unitario", "Total"
    ])

def guardar_venta(df):
    df.to_csv(CSV_PATH, index=False)

st.title("CHICANEROS — Registro de Ventas")

tab1, tab2, tab3 = st.tabs(["Nueva Venta", "Historial", "Resumen"])

with tab1:
    st.subheader("Registrar nueva venta")
    col1, col2 = st.columns([3, 1])
    with col1:
        producto = st.selectbox("Producto", list(MENU.keys()))
    with col2:
        cantidad = st.number_input("Cantidad", min_value=1, max_value=50, value=1)

    precio_unitario = MENU[producto]["precio"]
    total = precio_unitario * cantidad
    categoria = MENU[producto]["categoria"]

    st.markdown(f"**Precio unitario:** ${precio_unitario:,.0f}  |  **Total:** ${total:,.0f}")

    if st.button("Registrar Venta", use_container_width=True):
        df = cargar_ventas()
        nueva_fila = {
            "Fecha":           datetime.now().strftime("%Y-%m-%d"),
            "Hora":            datetime.now().strftime("%H:%M:%S"),
            "Producto":        producto,
            "Categoria":       categoria,
            "Cantidad":        cantidad,
            "Precio Unitario": precio_unitario,
            "Total":           total,
        }
        df = pd.concat([df, pd.DataFrame([nueva_fila])], ignore_index=True)
        guardar_venta(df)
        st.success(f"Registrado: {cantidad}x {producto} — ${total:,.0f}")
        st.rerun()

with tab2:
    st.subheader("Historial de Ventas")
    df = cargar_ventas()

    if df.empty:
        st.info("Aun no hay ventas registradas.")
    else:
        fechas = sorted(df["Fecha"].unique(), reverse=True)
        fecha_sel = st.selectbox("Filtrar por fecha", ["Todas"] + list(fechas))
        df_filtrado = df if fecha_sel == "Todas" else df[df["Fecha"] == fecha_sel]
        st.dataframe(df_filtrado, use_container_width=True)
        st.markdown(f"### Total del periodo: ${df_filtrado['Total'].sum():,.0f}")

        if st.button("Eliminar ultimo registro"):
            df_full = cargar_ventas()
            df_full = df_full.iloc[:-1]
            guardar_venta(df_full)
            st.warning("Ultimo registro eliminado.")
            st.rerun()

with tab3:
    st.subheader("Resumen General")
    df = cargar_ventas()

    if df.empty:
        st.info("Aun no hay ventas registradas.")
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Ventas Totales", f"${df['Total'].sum():,.0f}")
        with col2:
            st.metric("Transacciones", len(df))
        with col3:
            st.metric("Dias con ventas", df["Fecha"].nunique())

        st.markdown("---")

        st.markdown("#### Productos mas vendidos")
        top = df.groupby("Producto")["Cantidad"].sum().sort_values(ascending=False).reset_index()
        top.columns = ["Producto", "Unidades Vendidas"]
        st.dataframe(top, use_container_width=True)

        st.markdown("#### Ingresos por categoria")
        cat = df.groupby("Categoria")["Total"].sum().sort_values(ascending=False).reset_index()
        cat["Total"] = cat["Total"].apply(lambda x: f"${x:,.0f}")
        st.dataframe(cat, use_container_width=True)

        st.markdown("#### Ventas por dia")
        por_dia = df.groupby("Fecha")["Total"].sum().reset_index()
        st.bar_chart(por_dia.set_index("Fecha"))