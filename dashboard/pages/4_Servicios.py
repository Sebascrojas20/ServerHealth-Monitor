import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.title("⚙️ Servicios Windows")
st.caption("Supervisión del estado y configuración de servicios del sistema")

# Cargar último reporte
BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = BASE_DIR / "reportes"

archivos = sorted(
    REPORT_DIR.glob("reporte_servidor_*.csv"),
    key=lambda archivo: archivo.stat().st_mtime,
    reverse=True
)

if not archivos:
    st.warning("No se encontraron reportes CSV.")
    st.stop()

df = pd.read_csv(archivos[0])

if df.empty:
    st.warning("El reporte no contiene información.")
    st.stop()

equipo = df["Equipo"].iloc[0]
fecha = df["Fecha"].iloc[0]

st.subheader(f"🖥️ Servidor: {equipo}")
st.caption(f"Último monitoreo: {fecha}")

# Filtrar servicios
servicios = df[
    df["Categoria"].astype(str).str.contains(
        "servicio", case=False, na=False
    )
].copy()

if servicios.empty:
    st.warning("No se encontraron registros de servicios Windows.")
    st.stop()

# Normalizar estados
servicios["Estado"] = (
    servicios["Estado"].fillna("SIN ESTADO").astype(str).str.upper()
)

# Clasificar resultados
operativos = servicios[servicios["Estado"] == "OK"]

advertencias = servicios[
    servicios["Estado"] == "ADVERTENCIA"
]

errores = servicios[
    servicios["Estado"].isin(["ERROR", "CRITICO"])
]

otros = servicios[
    ~servicios["Estado"].isin(
        ["OK", "ADVERTENCIA", "ERROR", "CRITICO"]
    )
]

# Indicadores
st.divider()
st.subheader("Resumen de servicios")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total supervisados", len(servicios))
c2.metric("Operativos", len(operativos))
c3.metric("Advertencias", len(advertencias))
c4.metric("Errores / críticos", len(errores))

# Estado general
st.divider()
st.subheader("Estado general")

if not errores.empty:
    st.error("🔴 Se detectaron servicios con errores o estados críticos.")
elif not advertencias.empty or not otros.empty:
    st.warning("🟡 Algunos servicios requieren revisión.")
else:
    st.success("🟢 Todos los servicios supervisados están operativos.")

# Distribución
st.divider()
st.subheader("Distribución de estados")

distribucion = (
    servicios["Estado"]
    .value_counts()
    .rename_axis("Estado")
    .reset_index(name="Cantidad")
)

fig = px.pie(
    distribucion,
    names="Estado",
    values="Cantidad",
    hole=0.45
)

st.plotly_chart(fig, use_container_width=True)

# Detalle de servicios
st.divider()
st.subheader("Detalle de servicios supervisados")

columnas = [
    columna for columna in
    ["Elemento", "Detalle", "Estado", "TiempoMs"]
    if columna in servicios.columns
]

st.dataframe(
    servicios[columnas],
    use_container_width=True,
    hide_index=True
)

# Filtro por estado
st.divider()
st.subheader("Filtrar servicios")

estados = ["Todos"] + sorted(
    servicios["Estado"].dropna().unique().tolist()
)

seleccion = st.selectbox("Estado del servicio", estados)

if seleccion != "Todos":
    filtrados = servicios[servicios["Estado"] == seleccion]
else:
    filtrados = servicios

st.dataframe(
    filtrados[columnas],
    use_container_width=True,
    hide_index=True
)

st.caption("ServerHealth Monitor | Supervisión de servicios Windows")
