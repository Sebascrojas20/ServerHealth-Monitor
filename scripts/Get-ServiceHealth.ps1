# ============================================================
# ServerHealth Monitor
# Version: 1.0
# Module: Windows Services Monitoring
# Compatibility: Windows PowerShell 5.1
# ============================================================

param([switch]$AsObject)

$ErrorActionPreference = "Stop"

$ServiciosEsperados = @(
    "EventLog",
    "Winmgmt",
    "Schedule",
    "Dnscache",
    "LanmanWorkstation"
)

$Resultados = @()

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       WINDOWS SERVICES MONITOR           " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

foreach ($Nombre in $ServiciosEsperados) {

    try {
        $Servicio = Get-CimInstance Win32_Service `
            -Filter "Name='$Nombre'" `
            -ErrorAction Stop

        if ($null -eq $Servicio) {
            throw "Servicio no encontrado."
        }

        $Estado = if ($Servicio.State -eq "Running") {
            "OK"
        }
        elseif ($Servicio.State -eq "Stopped") {
            "ADVERTENCIA"
        }
        else {
            "ADVERTENCIA"
        }

        $Resultados += [PSCustomObject]@{
            Servicio = $Servicio.DisplayName
            Nombre = $Nombre
            Estado = $Servicio.State
            Inicio = $Servicio.StartMode
            Resultado = $Estado
        }
    }
    catch {
        $Resultados += [PSCustomObject]@{
            Servicio = $Nombre
            Nombre = $Nombre
            Estado = "No disponible"
            Inicio = "Desconocido"
            Resultado = "ERROR"
        }
    }
}

Write-Host "EQUIPO: $env:COMPUTERNAME"
Write-Host "FECHA: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

if (-not $AsObject) {
    $Resultados | Format-Table -AutoSize -Wrap
}

$Correctos = @($Resultados | Where-Object {
    $_.Resultado -eq "OK"
}).Count

$Advertencias = @($Resultados | Where-Object {
    $_.Resultado -eq "ADVERTENCIA"
}).Count

$Errores = @($Resultados | Where-Object {
    $_.Resultado -eq "ERROR"
}).Count

Write-Host "RESUMEN DE SERVICIOS" -ForegroundColor Cyan
Write-Host "Total revisados: $($Resultados.Count)"
Write-Host "Funcionando: $Correctos"
Write-Host "Advertencias: $Advertencias"
Write-Host "Errores: $Errores"

if ($Errores -gt 0) {
    Write-Host "`nRESULTADO: ERROR DE CONSULTA" -ForegroundColor Red
}
elseif ($Advertencias -gt 0) {
    Write-Host "`nRESULTADO: REQUIERE REVISION" -ForegroundColor Yellow
}
else {
    Write-Host "`nRESULTADO: SERVICIOS NORMALES" -ForegroundColor Green
}

Write-Host ""
Write-Host "Monitoreo de servicios finalizado."


if ($AsObject) { $Resultados; return }
