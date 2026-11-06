import streamlit as st
import pandas as pd
import plotly.express as px
import re
from pathlib import Path

st.title("🖥️ Recursos")
st.caption("Supervisión de CPU, memoria RAM y almacenamiento")

# Localizar reportes
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
    st.warning("El reporte seleccionado no contiene información.")
    st.stop()

equipo = df["Equipo"].iloc[0]
fecha = df["Fecha"].iloc[0]

st.subheader(f"Servidor: {equipo}")
st.caption(f"Último monitoreo: {fecha}")

# Filtrar recursos
recursos = df[
    df["Categoria"].astype(str).str.contains(
        "CPU, RAM y discos", case=False, na=False
    )
].copy()

if recursos.empty:
    st.warning("No se encontraron registros de CPU, RAM o discos.")
    st.stop()

# Extraer porcentajes
def obtener_porcentaje(detalle):
    coincidencia = re.search(
        r"(\d+(?:[.,]\d+)?)\s*%",
        str(detalle)
    )

    if coincidencia:
        return float(coincidencia.group(1).replace(",", "."))

    return None

recursos["Porcentaje"] = recursos["Detalle"].apply(obtener_porcentaje)

# CPU y RAM
cpu = recursos[recursos["Elemento"].astype(str).str.upper() == "CPU"]
ram = recursos[recursos["Elemento"].astype(str).str.upper() == "RAM"]

st.divider()
st.subheader("Uso de recursos")

c1, c2 = st.columns(2)

if not cpu.empty and pd.notna(cpu["Porcentaje"].iloc[0]):
    valor_cpu = cpu["Porcentaje"].iloc[0]
    c1.metric("Uso de CPU", f"{valor_cpu:.2f} %")
else:
    c1.metric("Uso de CPU", "Sin datos")

if not ram.empty and pd.notna(ram["Porcentaje"].iloc[0]):
    valor_ram = ram["Porcentaje"].iloc[0]
    c2.metric("Uso de RAM", f"{valor_ram:.2f} %")
else:
    c2.metric("Uso de RAM", "Sin datos")

# Gráfico CPU y RAM
comparacion = []

if not cpu.empty and pd.notna(cpu["Porcentaje"].iloc[0]):
    comparacion.append({
        "Recurso": "CPU",
        "Uso (%)": cpu["Porcentaje"].iloc[0]
    })

if not ram.empty and pd.notna(ram["Porcentaje"].iloc[0]):
    comparacion.append({
        "Recurso": "RAM",
        "Uso (%)": ram["Porcentaje"].iloc[0]
    })

if comparacion:
    st.subheader("Comparación de consumo")

    fig = px.bar(
        pd.DataFrame(comparacion),
        x="Recurso",
        y="Uso (%)",
        text="Uso (%)",
        range_y=[0, 100]
    )

    st.plotly_chart(fig, use_container_width=True)

# Discos
st.divider()
st.subheader("Almacenamiento")

discos = recursos[
    recursos["Elemento"].astype(str).str.startswith(
        "Disco", na=False
    )
].copy()

if not discos.empty:
    discos = discos.dropna(subset=["Porcentaje"])

    if not discos.empty:
        discos["Unidad"] = discos["Elemento"]

        fig_discos = px.bar(
            discos,
            x="Unidad",
            y="Porcentaje",
            text="Porcentaje",
            range_y=[0, 100],
            labels={"Porcentaje": "Espacio libre (%)"}
        )

        st.plotly_chart(fig_discos, use_container_width=True)

        st.dataframe(
            discos[["Elemento", "Detalle", "Estado"]],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No se encontraron porcentajes de almacenamiento.")
else:
    st.info("No se encontraron registros de discos.")

st.caption("ServerHealth Monitor | Monitoreo de recursos")
