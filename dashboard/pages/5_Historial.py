import streamlit as st
import pandas as pd
import plotly.express as px
import re
from pathlib import Path

st.title("📈 Historial")
st.caption("Evolución histórica de los recursos de infraestructura")

# Buscar reportes
BASE_DIR = Path(__file__).resolve().parents[2]
REPORT_DIR = BASE_DIR / "reportes"

archivos = sorted(
    REPORT_DIR.glob("reporte_servidor_*.csv"),
    key=lambda archivo: archivo.stat().st_mtime
)

if not archivos:
    st.warning("No se encontraron reportes CSV.")
    st.stop()

# Extraer porcentaje de los detalles
def obtener_porcentaje(detalle):
    coincidencia = re.search(
        r"(\d+(?:[.,]\d+)?)\s*%",
        str(detalle)
    )

    if coincidencia:
        return float(coincidencia.group(1).replace(",", "."))

    return None

# Consolidar información histórica
registros = []

for archivo in archivos:
    try:
        df = pd.read_csv(archivo)

        if df.empty:
            continue

        for _, fila in df.iterrows():
            categoria = str(fila.get("Categoria", ""))
            elemento = str(fila.get("Elemento", ""))
            detalle = fila.get("Detalle", "")

            if "CPU, RAM y discos" not in categoria:
                continue

            porcentaje = obtener_porcentaje(detalle)

            if porcentaje is None:
                continue

            elemento_upper = elemento.upper()

            if elemento_upper == "CPU":
                tipo = "CPU"
                unidad = "CPU"
            elif elemento_upper == "RAM":
                tipo = "RAM"
                unidad = "RAM"
            elif elemento_upper.startswith("DISCO"):
                tipo = "Discos"
                unidad = elemento
            else:
                continue

            registros.append({
                "Fecha": fila.get("Fecha"),
                "Equipo": fila.get("Equipo"),
                "Tipo": tipo,
                "Unidad": unidad,
                "Porcentaje": porcentaje,
                "Estado": fila.get("Estado"),
                "Archivo": archivo.name
            })

    except Exception as error:
        st.warning(f"No se pudo leer {archivo.name}: {error}")

if not registros:
    st.warning("No hay registros históricos de recursos disponibles.")
    st.stop()

historico = pd.DataFrame(registros)

historico["Fecha"] = pd.to_datetime(
    historico["Fecha"],
    errors="coerce"
)

historico = historico.dropna(subset=["Fecha", "Porcentaje"])
historico = historico.sort_values("Fecha")

if historico.empty:
    st.warning("No se encontraron fechas válidas en los reportes.")
    st.stop()

# Información general
equipos = historico["Equipo"].dropna().unique()

st.divider()

c1, c2, c3 = st.columns(3)

c1.metric("Reportes encontrados", len(archivos))
c2.metric("Registros históricos", len(historico))
c3.metric("Equipos registrados", len(equipos))

st.caption(
    f"Periodo disponible: "
    f"{historico['Fecha'].min():%d/%m/%Y %H:%M} "
    f"hasta {historico['Fecha'].max():%d/%m/%Y %H:%M}"
)

# Selección del recurso
st.divider()
st.subheader("Consultar evolución")

opciones = ["CPU", "RAM", "Discos"]
seleccion = st.selectbox("Seleccionar recurso", opciones)

datos = historico[historico["Tipo"] == seleccion].copy()

if datos.empty:
    st.info(f"No hay registros históricos disponibles para {seleccion}.")
    st.stop()

# CPU y RAM
if seleccion in ["CPU", "RAM"]:
    datos = datos.sort_values("Fecha")

    ultimo = datos.iloc[-1]["Porcentaje"]
    promedio = datos["Porcentaje"].mean()
    maximo = datos["Porcentaje"].max()

    c1, c2, c3 = st.columns(3)

    c1.metric("Último registro", f"{ultimo:.2f} %")
    c2.metric("Promedio histórico", f"{promedio:.2f} %")
    c3.metric("Máximo registrado", f"{maximo:.2f} %")

    fig = px.line(
        datos,
        x="Fecha",
        y="Porcentaje",
        markers=True,
        title=f"Evolución histórica de {seleccion}",
        labels={
            "Fecha": "Fecha del monitoreo",
            "Porcentaje": "Uso (%)"
        }
    )

    fig.update_yaxes(range=[0, 100])

    st.plotly_chart(fig, use_container_width=True)

# Discos
else:
    unidades = sorted(datos["Unidad"].unique().tolist())

    unidad_seleccionada = st.selectbox(
        "Seleccionar unidad",
        unidades
    )

    datos_unidad = datos[
        datos["Unidad"] == unidad_seleccionada
    ].sort_values("Fecha")

    if not datos_unidad.empty:
        ultimo = datos_unidad.iloc[-1]["Porcentaje"]
        promedio = datos_unidad["Porcentaje"].mean()
        minimo = datos_unidad["Porcentaje"].min()

        c1, c2, c3 = st.columns(3)

        c1.metric("Último espacio libre", f"{ultimo:.2f} %")
        c2.metric("Promedio histórico", f"{promedio:.2f} %")
        c3.metric("Mínimo registrado", f"{minimo:.2f} %")

        fig = px.line(
            datos_unidad,
            x="Fecha",
            y="Porcentaje",
            markers=True,
            title=f"Evolución del espacio libre - {unidad_seleccionada}",
            labels={
                "Fecha": "Fecha del monitoreo",
                "Porcentaje": "Espacio libre (%)"
            }
        )

        fig.update_yaxes(range=[0, 100])

        st.plotly_chart(fig, use_container_width=True)

# Comparación de recursos
st.divider()
st.subheader("Comparación de CPU y RAM")

comparacion = historico[
    historico["Tipo"].isin(["CPU", "RAM"])
]

if not comparacion.empty:
    fig_comparacion = px.line(
        comparacion,
        x="Fecha",
        y="Porcentaje",
        color="Tipo",
        markers=True,
        labels={
            "Fecha": "Fecha del monitoreo",
            "Porcentaje": "Uso (%)",
            "Tipo": "Recurso"
        }
    )

    fig_comparacion.update_yaxes(range=[0, 100])

    st.plotly_chart(
        fig_comparacion,
        use_container_width=True
    )
else:
    st.info("No hay datos suficientes para comparar CPU y RAM.")

# Tabla histórica
st.divider()
st.subheader("Registros históricos")

st.dataframe(
    datos.sort_values("Fecha", ascending=False),
    use_container_width=True,
    hide_index=True
)

st.caption("ServerHealth Monitor | Histórico de infraestructura")
