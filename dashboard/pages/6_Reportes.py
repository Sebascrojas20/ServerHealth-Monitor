import streamlit as st
import pandas as pd
from pathlib import Path

st.title("📁 Reportes")
st.caption("Consulta, visualización y descarga de informes de monitoreo")

# Directorio de reportes
BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = BASE_DIR / "reportes"

# Buscar archivos
archivos_csv = sorted(
    REPORT_DIR.glob("reporte_servidor_*.csv"),
    key=lambda archivo: archivo.stat().st_mtime,
    reverse=True
)

archivos_html = {
    archivo.stem: archivo
    for archivo in REPORT_DIR.glob("reporte_servidor_*.html")
}

if not archivos_csv:
    st.warning("No se encontraron reportes CSV.")
    st.stop()

# Seleccionar reporte
st.divider()
st.subheader("Seleccionar informe")

seleccionado = st.selectbox(
    "Historial de reportes",
    archivos_csv,
    format_func=lambda archivo: archivo.name
)

# Cargar información
try:
    df = pd.read_csv(seleccionado)
except Exception as error:
    st.error(f"No se pudo leer el reporte: {error}")
    st.stop()

if df.empty:
    st.warning("El reporte seleccionado no contiene registros.")
    st.stop()

# Información general
equipo = df["Equipo"].iloc[0]
fecha = df["Fecha"].iloc[0]

st.subheader(f"🖥️ Servidor: {equipo}")
st.caption(f"Fecha del monitoreo: {fecha}")

# Indicadores
estados = df["Estado"].fillna("").astype(str).str.upper()

total = len(df)
correctos = estados.isin(["OK", "DISPONIBLE"]).sum()
no_disponibles = (estados == "NO DISPONIBLE").sum()
advertencias = (estados == "ADVERTENCIA").sum()
criticos = (estados == "CRITICO").sum()
errores = (estados == "ERROR").sum()

st.divider()
st.subheader("Resumen del informe")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Registros", total)
c2.metric("Correctos", correctos)
c3.metric("No disponibles", no_disponibles)
c4.metric("Advertencias", advertencias)

c5, c6 = st.columns(2)

c5.metric("Críticos", criticos)
c6.metric("Errores", errores)

# Descargas
st.divider()
st.subheader("Descargar archivos")

col1, col2 = st.columns(2)

with col1:
    csv_bytes = seleccionado.read_bytes()

    st.download_button(
        label="⬇️ Descargar CSV",
        data=csv_bytes,
        file_name=seleccionado.name,
        mime="text/csv",
        use_container_width=True
    )

with col2:
    html_archivo = archivos_html.get(seleccionado.stem)

    if html_archivo and html_archivo.exists():
        html_bytes = html_archivo.read_bytes()

        st.download_button(
            label="⬇️ Descargar HTML",
            data=html_bytes,
            file_name=html_archivo.name,
            mime="text/html",
            use_container_width=True
        )
    else:
        st.info("No existe un HTML asociado a este reporte.")

# Vista previa HTML
st.divider()
st.subheader("Vista previa del informe HTML")

if html_archivo and html_archivo.exists():
    contenido_html = html_archivo.read_text(encoding="utf-8-sig")

    with st.expander("Abrir informe HTML", expanded=False):
        st.components.v1.html(
            contenido_html,
            height=750,
            scrolling=True
        )
else:
    st.info("No hay vista previa disponible para este reporte.")

# Tabla de registros
st.divider()
st.subheader("Detalle de registros")

categorias = ["Todas"] + sorted(
    df["Categoria"].dropna().unique().tolist()
)

categoria = st.selectbox(
    "Filtrar por categoría",
    categorias
)

if categoria != "Todas":
    df_filtrado = df[df["Categoria"] == categoria]
else:
    df_filtrado = df

st.dataframe(
    df_filtrado,
    use_container_width=True,
    hide_index=True
)

st.caption("ServerHealth Monitor | Gestión de reportes")
