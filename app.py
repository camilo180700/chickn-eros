import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime
import io

st.set_page_config(
    page_title="CHICANEROS",
    page_icon="🍗",
    layout="wide"
)

# CSS para mejor diseño móvil
st.markdown("""
<style>
    .stButton > button { height: 3em; font-size: 1.05em; }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 15px;
    }
</style>
""", unsafe_allow_html=True)

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

HEADERS = ["Orden", "Fecha", "Hora", "Producto", "Categoria",
           "Cantidad", "Precio Unitario", "Total"]

if "carrito" not in st.session_state:
    st.session_state.carrito = []

@st.cache_resource
def get_client():
    credentials = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=[
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
    )
    return gspread.authorize(credentials)

def get_sheet():
    return get_client().open("CHICANEROS_ventas").sheet1

def cargar_ventas():
    sheet = get_sheet()
    data = sheet.get_all_records()
    if data:
        return pd.DataFrame(data)
    return pd.DataFrame(columns=HEADERS)

def registrar_orden(carrito):
    sheet = get_sheet()
    fecha = datetime.now().strftime("%Y-%m-%d")
    hora  = datetime.now().strftime("%H:%M:%S")
    orden_id = datetime.now().strftime("%Y%m%d%H%M%S")
    for item in carrito:
        sheet.append_row([
            orden_id, fecha, hora,
            item["producto"], item["categoria"],
            item["cantidad"], item["precio_unitario"], item["total"]
        ])
    return orden_id

def eliminar_ultimo():
    sheet = get_sheet()
    ultima = len(sheet.get_all_values())
    if ultima > 1:
        sheet.delete_rows(ultima)

# ── TÍTULO ──────────────────────────────────────────────────────────
st.title("CHICANEROS — Registro de Ventas")

tab1, tab2, tab3 = st.tabs(["Nueva Venta", "Historial", "Resumen"])

# ── TAB 1: CARRITO ──────────────────────────────────────────────────
with tab1:
    st.subheader("Armar pedido")

    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        producto = st.selectbox("Producto", list(MENU.keys()))
    with col2:
        cantidad = st.number_input("Cant.", min_value=1, max_value=50, value=1)
    with col3:
        st.write("")
        st.write("")
        if st.button("Agregar", use_container_width=True):
            encontrado = False
            for item in st.session_state.carrito:
                if item["producto"] == producto:
                    item["cantidad"] += cantidad
                    item["total"] = item["cantidad"] * item["precio_unitario"]
                    encontrado = True
                    break
            if not encontrado:
                st.session_state.carrito.append({
                    "producto":        producto,
                    "categoria":       MENU[producto]["categoria"],
                    "cantidad":        cantidad,
                    "precio_unitario": MENU[producto]["precio"],
                    "total":           MENU[producto]["precio"] * cantidad
                })
            st.rerun()

    st.markdown("---")
    st.subheader("Pedido actual")

    if not st.session_state.carrito:
        st.info("El carrito está vacío. Agrega productos arriba.")
    else:
        total_pedido = 0
        for i, item in enumerate(st.session_state.carrito):
            c1, c2, c3, c4 = st.columns([4, 1, 2, 1])
            with c1: st.write(f"**{item['producto']}**")
            with c2: st.write(f"x{item['cantidad']}")
            with c3: st.write(f"${item['total']:,.0f}")
            with c4:
                if st.button("✕", key=f"del_{i}"):
                    st.session_state.carrito.pop(i)
                    st.rerun()
            total_pedido += item["total"]

        st.markdown("---")
        st.markdown(f"## Total: ${total_pedido:,.0f}")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Vaciar carrito", use_container_width=True):
                st.session_state.carrito = []
                st.rerun()
        with c2:
            if st.button("Registrar Pedido", use_container_width=True, type="primary"):
                registrar_orden(st.session_state.carrito)
                st.session_state.carrito = []
                st.success(f"Pedido registrado — Total: ${total_pedido:,.0f}")
                st.rerun()

# ── TAB 2: HISTORIAL ────────────────────────────────────────────────
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

        # Exportar Excel
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            df_filtrado.to_excel(writer, index=False, sheet_name="Ventas")
        buffer.seek(0)
        st.download_button(
            label="Descargar Excel",
            data=buffer,
            file_name=f"ventas_chicaneros_{fecha_sel}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

        if st.button("Eliminar ultimo registro"):
            eliminar_ultimo()
            st.warning("Ultimo registro eliminado.")
            st.rerun()

# ── TAB 3: RESUMEN ──────────────────────────────────────────────────
with tab3:
    st.subheader("Resumen General")
    df = cargar_ventas()

    if df.empty:
        st.info("Aun no hay ventas registradas.")
    else:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Ventas Totales", f"${df['Total'].sum():,.0f}")
        with c2:
            pedidos = df["Orden"].nunique() if "Orden" in df.columns else len(df)
            st.metric("Pedidos", pedidos)
        with c3:
            st.metric("Dias con ventas", df["Fecha"].nunique())

        st.markdown("---")

        st.markdown("#### Ventas por dia")
        por_dia = df.groupby("Fecha")["Total"].sum().reset_index()
        st.bar_chart(por_dia.set_index("Fecha"), color="#FF6B35")

        st.markdown("#### Productos mas vendidos (unidades)")
        top = df.groupby("Producto")["Cantidad"].sum().sort_values(ascending=False).reset_index()
        st.bar_chart(top.set_index("Producto"), color="#FFB347")

        st.markdown("#### Ingresos por categoria")
        cat = df.groupby("Categoria")["Total"].sum().sort_values(ascending=False).reset_index()
        st.bar_chart(cat.set_index("Categoria"), color="#4CAF50")
