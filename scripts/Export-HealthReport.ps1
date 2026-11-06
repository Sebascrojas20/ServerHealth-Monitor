# ============================================================
# ServerHealth Monitor
# Module: HTML and CSV Report Generator
# Compatibility: Windows PowerShell 5.1
# ============================================================

$ErrorActionPreference = "Stop"

$Proyecto = Split-Path $PSScriptRoot -Parent
$CarpetaReportes = Join-Path $Proyecto "reportes"

if (-not (Test-Path $CarpetaReportes)) {
    New-Item -Path $CarpetaReportes -ItemType Directory -Force | Out-Null
}

$Fecha = Get-Date
$Equipo = $env:COMPUTERNAME
$MarcaTiempo = $Fecha.ToString("yyyyMMdd_HHmmss")

$Resultados = @()

$Modulos = @(
    @{
        Nombre = "CPU, RAM y discos"
        Archivo = "Get-ServerHealth.ps1"
        Tipo = "RECURSO"
    },
    @{
        Nombre = "Servicios Windows"
        Archivo = "Get-ServiceHealth.ps1"
        Tipo = "SERVICIO"
    },
    @{
        Nombre = "Conectividad"
        Archivo = "Test-ServerConnectivity.ps1"
        Tipo = "RED"
    }
)

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       SERVER HEALTH REPORT GENERATOR     " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

foreach ($Modulo in $Modulos) {

    $RutaModulo = Join-Path $PSScriptRoot $Modulo.Archivo

    if (-not (Test-Path $RutaModulo)) {
        throw "No se encuentra el modulo: $RutaModulo"
    }

    Write-Host "`nEjecutando: $($Modulo.Nombre)" -ForegroundColor Yellow

    $Datos = @(& $RutaModulo -AsObject)

    if ($Datos.Count -eq 0) {
        throw "El modulo no devolvio resultados: $($Modulo.Archivo)"
    }

    foreach ($Dato in $Datos) {

        $Elemento = ""
        $Detalle = ""
        $Estado = ""
        $TiempoMs = ""

        switch ($Modulo.Tipo) {

            "RECURSO" {
                $Elemento = $Dato.Recurso
                $Detalle = $Dato.Valor
                $Estado = $Dato.Estado
            }

            "SERVICIO" {
                $Elemento = $Dato.Servicio
                $Detalle = "Nombre: $($Dato.Nombre) | Inicio: $($Dato.Inicio) | Estado: $($Dato.Estado)"
                $Estado = $Dato.Resultado
            }

            "RED" {
                $Elemento = $Dato.Categoria
                $Detalle = "Destino: $($Dato.Destino) | Puerto: $($Dato.Puerto)"
                $Estado = $Dato.Estado
                $TiempoMs = $Dato.TiempoMs
            }
        }

        $Resultados += [PSCustomObject]@{
            Equipo = $Equipo
            Categoria = $Modulo.Nombre
            Elemento = $Elemento
            Detalle = $Detalle
            Estado = $Estado
            TiempoMs = $TiempoMs
            Fecha = $Fecha.ToString("yyyy-MM-dd HH:mm:ss")
        }
    }
}

# ------------------------------------------------------------
# RESUMEN GENERAL
# ------------------------------------------------------------

$Total = $Resultados.Count

$Criticos = @($Resultados | Where-Object {
    $_.Estado -eq "CRITICO"
}).Count

$Advertencias = @($Resultados | Where-Object {
    $_.Estado -eq "ADVERTENCIA"
}).Count

$Errores = @($Resultados | Where-Object {
    $_.Estado -eq "ERROR"
}).Count

$NoDisponibles = @($Resultados | Where-Object {
    $_.Estado -eq "NO DISPONIBLE"
}).Count

$Correctos = @($Resultados | Where-Object {
    $_.Estado -eq "OK" -or $_.Estado -eq "DISPONIBLE"
}).Count

if ($Criticos -gt 0 -or $Errores -gt 0) {
    $EstadoGeneral = "CRITICO"
}
elseif ($Advertencias -gt 0) {
    $EstadoGeneral = "ADVERTENCIA"
}
else {
    $EstadoGeneral = "NORMAL"
}

# ------------------------------------------------------------
# EXPORTAR CSV
# ------------------------------------------------------------

$RutaCSV = Join-Path $CarpetaReportes "reporte_servidor_$MarcaTiempo.csv"

$Resultados | Export-Csv `
    -Path $RutaCSV `
    -NoTypeInformation `
    -Encoding UTF8

# ------------------------------------------------------------
# GENERAR HTML
# ------------------------------------------------------------

$RutaHTML = Join-Path $CarpetaReportes "reporte_servidor_$MarcaTiempo.html"

$Estilos = @"
<style>
body {
    font-family: Segoe UI, Arial, sans-serif;
    background: #f3f5f8;
    color: #263238;
    margin: 30px;
}
h1 { color: #17365d; }
h2 { color: #334e68; }
table {
    border-collapse: collapse;
    width: 100%;
    background: white;
    margin-top: 15px;
}
th {
    background: #17365d;
    color: white;
    padding: 12px;
    text-align: left;
}
td {
    border: 1px solid #dce2e8;
    padding: 10px;
}
tr:nth-child(even) { background: #f2f6fa; }
.normal { color: #16803c; font-weight: bold; }
.warning { color: #b7791f; font-weight: bold; }
.critical { color: #c53030; font-weight: bold; }
.summary {
    background: white;
    padding: 18px;
    border-radius: 8px;
    margin-bottom: 20px;
}
.footer {
    margin-top: 25px;
    color: #687782;
    font-size: 12px;
}
</style>
"@

$ClaseEstado = switch ($EstadoGeneral) {
    "NORMAL" { "normal" }
    "ADVERTENCIA" { "warning" }
    "CRITICO" { "critical" }
}

$ResumenHTML = @"
<div class='summary'>
<h2>Resumen general: <span class='$ClaseEstado'>$EstadoGeneral</span></h2>
<p><b>Equipo:</b> $Equipo</p>
<p><b>Fecha:</b> $($Fecha.ToString("yyyy-MM-dd HH:mm:ss"))</p>
<p><b>Registros:</b> $Total</p>
<p><b>Correctos:</b> $Correctos |
<b>Advertencias:</b> $Advertencias |
<b>Críticos:</b> $Criticos |
<b>Errores:</b> $Errores |
<b>No disponibles:</b> $NoDisponibles</p>
</div>
"@

$PieHTML = @"
<div class='footer'>
<p>ServerHealth Monitor | Informe generado automáticamente.</p>
<p>Este informe contiene resultados de monitoreo; no ejecuta cambios en el sistema.</p>
</div>
"@

$TablaHTML = $Resultados |
    ConvertTo-Html `
        -Property Equipo,Categoria,Elemento,Detalle,Estado,TiempoMs,Fecha `
        -Head $Estilos `
        -Title "ServerHealth Monitor - $Equipo" `
        -PreContent $ResumenHTML `
        -PostContent $PieHTML

$TablaHTML | Out-File -FilePath $RutaHTML -Encoding UTF8

# ------------------------------------------------------------
# RESULTADO
# ------------------------------------------------------------

Write-Host "`n========== GENERACION COMPLETADA ==========" -ForegroundColor Cyan
Write-Host "Equipo: $Equipo"
Write-Host "Registros: $Total"
Write-Host "Estado general: $EstadoGeneral"
Write-Host ""
Write-Host "HTML: $RutaHTML" -ForegroundColor Green
Write-Host "CSV:  $RutaCSV" -ForegroundColor Green
Write-Host "`nGeneracion finalizada."
