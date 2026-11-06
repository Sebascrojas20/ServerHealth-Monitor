$Proyecto = "$env:USERPROFILE\\OneDrive\\Documents\\Portafolio-TI\\02-Automatizacion\\ServerHealth-Monitor"



$Contenido = @'

\# ServerHealth-Monitor



Sistema de monitoreo de infraestructura Windows desarrollado con PowerShell y Python.



Permite consultar recursos del sistema, verificar servicios, diagnosticar conectividad y generar reportes mediante un dashboard interactivo.



\## Características



\- Monitoreo de CPU, memoria RAM y discos.

\- Verificación de servicios de Windows.

\- Diagnóstico de conectividad de red.

\- Comprobación de DNS e Internet.

\- Validación de puertos TCP.

\- Generación de reportes CSV y HTML.

\- Historial de mediciones.

\- Dashboard interactivo con Streamlit.



\## Tecnologías



| Tecnología | Uso |

|---|---|

| PowerShell | Monitoreo del sistema |

| Python | Aplicación principal |

| Streamlit | Dashboard |

| Pandas | Procesamiento de datos |

| Plotly | Gráficos |



\## Estructura



```text

ServerHealth-Monitor/

├── scripts/

├── config/

├── reportes/

├── logs/

├── evidencias/

├── ejemplos/

├── documentacion/

└── dashboard/

&#x20;   ├── app.py

&#x20;   └── pages/
