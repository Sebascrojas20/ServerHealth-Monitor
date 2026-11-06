import streamlit as st
import pandas as pd
from pathlib import Path

st.title("📊 Inicio")
st.caption("Resumen general del estado de la infraestructura")

# Ubicación de los reportes
BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = BASE_DIR / "reportes"

# Buscar reportes CSV
archivos = sorted(
    REPORT_DIR.glob("reporte_servidor_*.csv"),
    key=lambda archivo: archivo.stat().st_mtime,
    reverse=True
)

if not archivos:
    st.warning("No se encontraron reportes CSV.")
    st.stop()

# Cargar el último reporte
seleccionado = archivos[0]
df = pd.read_csv(seleccionado)

if df.empty:
    st.warning("El último reporte no contiene registros.")
    st.stop()

# Información del servidor
equipo = df["Equipo"].iloc[0]
fecha = df["Fecha"].iloc[0]

st.subheader(f"🖥️ Servidor: {equipo}")
st.caption(f"Último monitoreo: {fecha}")
st.caption(f"Archivo: {seleccionado.name}")

# Contabilizar estados
estados = df["Estado"].fillna("").astype(str).str.upper()

total = len(df)
correctos = estados.isin(["OK", "DISPONIBLE"]).sum()
no_disponibles = (estados == "NO DISPONIBLE").sum()
advertencias = (estados == "ADVERTENCIA").sum()
criticos = (estados == "CRITICO").sum()
errores = (estados == "ERROR").sum()

# Indicadores
st.divider()
st.subheader("Indicadores del monitoreo")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total de registros", total)
c2.metric("Correctos", correctos)
c3.metric("No disponibles", no_disponibles)
c4.metric("Advertencias", advertencias)

c5, c6 = st.columns(2)

c5.metric("Críticos", criticos)
c6.metric("Errores", errores)

# Estado general
st.divider()
st.subheader("Estado general")

if criticos > 0 or errores > 0:
    st.error("🔴 ESTADO CRÍTICO: se detectaron errores o elementos críticos.")
elif advertencias > 0:
    st.warning("🟡 ESTADO CON ADVERTENCIAS: revisar los elementos señalados.")
else:
    st.success("🟢 ESTADO NORMAL: no se detectaron advertencias ni errores.")

# Novedades
st.divider()
st.subheader("Novedades detectadas")

novedades = df[
    ~estados.isin(["OK", "DISPONIBLE"])
].copy()

if novedades.empty:
    st.success("No hay novedades que requieran revisión.")
else:
    st.dataframe(
        novedades,
        use_container_width=True,
        hide_index=True
    )

# Información del reporte
st.divider()
st.subheader("Información del reporte")

col1, col2 = st.columns(2)

col1.write(f"**Nombre:** {seleccionado.name}")
col2.write(f"**Tamaño:** {seleccionado.stat().st_size / 1024:.2f} KB")

st.caption("ServerHealth Monitor | Portafolio de Automatización TI")
