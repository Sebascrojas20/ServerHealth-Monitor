import streamlit as st

st.set_page_config(
    page_title="ServerHealth Monitor",
    page_icon="🖥️",
    layout="wide"
)

st.title("🖥️ ServerHealth Monitor")
st.caption("Plataforma de monitoreo de infraestructura Windows")

st.info("Selecciona un módulo desde el menú lateral para comenzar.")

st.subheader("Módulos disponibles")

modulos = [
    ("📊", "Inicio", "Resumen general de infraestructura."),
    ("🖥️", "Recursos", "CPU, memoria RAM y almacenamiento."),
    ("🌐", "Conectividad", "Gateway, DNS, Internet y puertos."),
    ("⚙️", "Servicios", "Supervisión de servicios Windows."),
    ("📈", "Historial", "Evolución histórica de los indicadores."),
    ("📁", "Reportes", "Consulta de informes CSV y HTML.")
]

for icono, nombre, descripcion in modulos:
    with st.container(border=True):
        st.markdown(f"### {icono} {nombre}")
        st.write(descripcion)

st.divider()
st.caption("ServerHealth Monitor | Portafolio de Automatización TI")
