# 📊 ServerHealth-Monitor v1.0

### Monitoreo de infraestructura Windows con PowerShell y Python

ServerHealth-Monitor es una herramienta desarrollada para recopilar, analizar y visualizar información del estado de servidores Windows.

Combina scripts de PowerShell para la recolección de información con un dashboard interactivo desarrollado en Python y Streamlit.

Su objetivo es facilitar la supervisión de recursos, servicios y conectividad, centralizando los resultados en reportes que permiten identificar posibles novedades en la infraestructura.

---

## 🎯 Funcionalidades principales

- **Monitoreo de recursos:** uso de CPU, memoria RAM y espacio disponible en discos.
- **Supervisión de servicios:** consulta del estado de servicios críticos de Windows.
- **Pruebas de conectividad:** validación de Gateway, DNS, conexión a Internet y puertos TCP.
- **Generación de reportes:** exportación de resultados en formatos CSV y HTML.
- **Historial:** consulta de resultados de ejecuciones anteriores.
- **Dashboard interactivo:** visualización de información mediante gráficos, indicadores y tablas.
- **Identificación de alertas:** clasificación de resultados según los niveles de estado definidos.

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Aplicación |
|---|---|
| PowerShell 5.1 | Recolección y análisis de información |
| Python | Procesamiento de datos |
| Streamlit | Dashboard interactivo |
| Pandas | Análisis de reportes |
| Plotly | Visualización de datos |
| CSV / HTML | Almacenamiento y presentación de resultados |

---

## 📁 Estructura del proyecto

```text
ServerHealth-Monitor/
│
├── scripts/
│   ├── Get-ServerHealth.ps1
│   ├── Get-ServiceHealth.ps1
│   ├── Test-ServerConnectivity.ps1
│   └── Export-HealthReport.ps1
│
├── dashboard/
│   ├── app.py
│   ├── pages/
│   ├── components/
│   └── utils/
│
├── config/
│   └── network.example.json
│
├── README.md
├── requirements.txt
└── .gitignore
```

---

## 📋 Requisitos

- Windows 10 o Windows Server.
- Windows PowerShell 5.1.
- Python 3.10 o superior.
- Permisos adecuados para consultar los recursos del equipo.
- Dependencias de Python instaladas.

---

## 🚀 Instalación

### 1. Clonar el repositorio

```powershell
git clone https://github.com/Sebascrojas20/ServerHealth-Monitor.git
```

### 2. Entrar al directorio

```powershell
cd ServerHealth-Monitor
```

### 3. Crear un entorno virtual

```powershell
python -m venv .venv
```

### 4. Activar el entorno virtual

```powershell
.\.venv\Scripts\Activate.ps1
```

### 5. Instalar dependencias

```powershell
pip install streamlit pandas plotly
```

---

## ▶️ Ejecución

### Generar reportes

Desde PowerShell:

```powershell
.\scripts\Export-HealthReport.ps1
```

Este proceso ejecuta las verificaciones disponibles y genera los reportes correspondientes.

### Iniciar el dashboard

```powershell
python -m streamlit run dashboard/app.py
```

Streamlit iniciará la aplicación y permitirá consultar los resultados desde el navegador.

---

## 📊 Secciones del dashboard

| Sección | Descripción |
|---|---|
| Inicio | Resumen general del estado del servidor |
| Recursos | Información de CPU, RAM y discos |
| Conectividad | Estado de conexiones y puertos TCP |
| Servicios | Supervisión de servicios de Windows |
| Historial | Evolución de resultados anteriores |
| Reportes | Consulta y descarga de archivos CSV y HTML |

---

## 🚦 Clasificación de estados

El sistema utiliza diferentes estados para facilitar la interpretación de los resultados:

- **NORMAL:** los indicadores cumplen las condiciones establecidas.
- **ADVERTENCIA:** se detectan condiciones que requieren revisión.
- **CRÍTICO:** se identifican condiciones críticas o errores.
- **NO DISPONIBLE:** una comprobación no pudo completarse o el recurso no respondió.

Los umbrales de CPU, RAM y almacenamiento están definidos en los scripts del proyecto.

---

## 🔐 Consideraciones de seguridad

- El proyecto realiza consultas de monitoreo y no inicia ni detiene servicios.
- Las configuraciones privadas deben mantenerse fuera del repositorio.
- No deben publicarse direcciones IP, credenciales ni información interna.
- Los reportes generados deben revisarse antes de compartirlos.

---

## 💡 Aplicación práctica

ServerHealth-Monitor demuestra cómo integrar PowerShell y Python para construir una solución de monitoreo de infraestructura tecnológica.

El proyecto permite centralizar información, facilitar el análisis de indicadores y generar reportes que apoyan las actividades de administración y soporte de servidores Windows.

---

## 👨‍💻 Autor

**Sebastián Rojas**

Técnico en Sistemas | Estudiante de Ingeniería de Sistemas

Intereses profesionales:

- Infraestructura TI.
- Administración de servidores.
- Automatización con PowerShell.
- Cloud Computing.
- Monitoreo y seguridad informática.

🔗 [GitHub](https://github.com/Sebascrojas20)

---

*Proyecto desarrollado con fines de aprendizaje, automatización y fortalecimiento de habilidades en administración de infraestructura tecnológica.*
