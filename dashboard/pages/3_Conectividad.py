import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.title("🌐 Conectividad")
st.caption("Diagnóstico de red, resolución DNS, acceso a Internet y puertos TCP")

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

# Filtrar registros de conectividad
conectividad = df[
    df["Categoria"].astype(str).str.contains(
        "Conectividad", case=False, na=False
    )
].copy()

if conectividad.empty:
    st.warning("No se encontraron registros de conectividad en el reporte.")
    st.stop()

# Normalizar estados
conectividad["Estado"] = (
    conectividad["Estado"].fillna("SIN ESTADO").astype(str).str.upper()
)

# Clasificar resultados
disponibles = conectividad[
    conectividad["Estado"].isin(["OK", "DISPONIBLE"])
]

no_disponibles = conectividad[
    conectividad["Estado"] == "NO DISPONIBLE"
]

advertencias = conectividad[
    conectividad["Estado"] == "ADVERTENCIA"
]

errores = conectividad[
    conectividad["Estado"].isin(["ERROR", "CRITICO"])
]

# Indicadores
st.divider()
st.subheader("Estado de conectividad")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Disponibles", len(disponibles))
c2.metric("No disponibles", len(no_disponibles))
c3.metric("Advertencias", len(advertencias))
c4.metric("Errores / críticos", len(errores))

# Diagnóstico de red principal
st.divider()
st.subheader("Diagnóstico de red")

principales = conectividad[
    conectividad["Elemento"].astype(str).str.contains(
        "Gateway|DNS|Internet",
        case=False,
        na=False
    )
].copy()

if not principales.empty:
    columnas = [
        columna for columna in
        ["Elemento", "Detalle", "Estado", "TiempoMs"]
        if columna in principales.columns
    ]

    st.dataframe(
        principales[columnas],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No se encontraron pruebas de Gateway, DNS o Internet.")

# Puertos TCP
st.divider()
st.subheader("Diagnóstico de puertos TCP")

puertos = conectividad[
    conectividad["Elemento"].astype(str).str.contains(
        "Puerto|TCP|HTTP|HTTPS|SQL|Oracle|RDP|SMB",
        case=False,
        na=False
    )
].copy()

if not puertos.empty:
    columnas = [
        columna for columna in
        ["Elemento", "Detalle", "Estado", "TiempoMs"]
        if columna in puertos.columns
    ]

    st.dataframe(
        puertos[columnas],
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No se encontraron pruebas de puertos TCP.")

# Distribución de estados
st.divider()
st.subheader("Distribución de resultados")

distribucion = (
    conectividad["Estado"]
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

# Tabla completa
st.divider()
st.subheader("Detalle completo de conectividad")

st.dataframe(
    conectividad,
    use_container_width=True,
    hide_index=True
)

st.caption("ServerHealth Monitor | Diagnóstico de conectividad")
