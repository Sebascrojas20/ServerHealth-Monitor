# ============================================================
# ServerHealth Monitor
# Version: 1.0
# Module: Network Connectivity
# Compatibility: Windows PowerShell 5.1
# ============================================================

param([switch]$AsObject)

$ErrorActionPreference = "Stop"

$RutaConfig = Join-Path $PSScriptRoot "..\config\network.example.json"

if (-not (Test-Path $RutaConfig)) {
    throw "No se encuentra el archivo de configuracion: $RutaConfig"
}

$Config = Get-Content $RutaConfig -Raw | ConvertFrom-Json

$Resultados = @()

function Test-TCPConnection {
    param(
        [string]$HostName,
        [int]$Port,
        [int]$Timeout = 3000
    )

    $Cliente = New-Object System.Net.Sockets.TcpClient
    $Cronometro = [System.Diagnostics.Stopwatch]::StartNew()

    try {
        $Conexion = $Cliente.BeginConnect($HostName, $Port, $null, $null)

        if (-not $Conexion.AsyncWaitHandle.WaitOne($Timeout, $false)) {
            throw "Tiempo de espera agotado"
        }

        $Cliente.EndConnect($Conexion)
        $Cronometro.Stop()

        return [PSCustomObject]@{
            Estado = "DISPONIBLE"
            TiempoMs = $Cronometro.ElapsedMilliseconds
        }
    }
    catch {
        $Cronometro.Stop()

        return [PSCustomObject]@{
            Estado = "NO DISPONIBLE"
            TiempoMs = $Cronometro.ElapsedMilliseconds
        }
    }
    finally {
        $Cliente.Close()
    }
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "      NETWORK CONNECTIVITY MONITOR        " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "EQUIPO: $env:COMPUTERNAME"
Write-Host "FECHA: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

# ------------------------------------------------------------
# 1. PUERTA DE ENLACE
# ------------------------------------------------------------

try {
    $Rutas = Get-NetRoute -DestinationPrefix "0.0.0.0/0" |
        Sort-Object RouteMetric

    $Gateway = $Rutas |
        Select-Object -First 1 -ExpandProperty NextHop

    if ([string]::IsNullOrWhiteSpace($Gateway)) {
        throw "No se encontro puerta de enlace."
    }

    $Ping = Test-Connection -ComputerName $Gateway -Count 1 -ErrorAction Stop

    $Resultados += [PSCustomObject]@{
        Categoria = "Gateway"
        Destino = $Gateway
        Puerto = "-"
        Estado = "DISPONIBLE"
        TiempoMs = [math]::Round($Ping.ResponseTime, 2)
    }
}
catch {
    $Resultados += [PSCustomObject]@{
        Categoria = "Gateway"
        Destino = "Puerta de enlace"
        Puerto = "-"
        Estado = "NO DISPONIBLE"
        TiempoMs = "-"
    }
}

# ------------------------------------------------------------
# 2. RESOLUCION DNS
# ------------------------------------------------------------

try {
    $Dns = Resolve-DnsName -Name $Config.DnsTest.Host `
        -ErrorAction Stop |
        Where-Object { $_.IPAddress } |
        Select-Object -First 1

    if ($null -eq $Dns) {
        throw "No se obtuvo direccion IP."
    }

    $Resultados += [PSCustomObject]@{
        Categoria = "DNS"
        Destino = $Config.DnsTest.Host
        Puerto = "-"
        Estado = "DISPONIBLE"
        TiempoMs = "-"
    }
}
catch {
    $Resultados += [PSCustomObject]@{
        Categoria = "DNS"
        Destino = $Config.DnsTest.Host
        Puerto = "-"
        Estado = "NO DISPONIBLE"
        TiempoMs = "-"
    }
}

# ------------------------------------------------------------
# 3. CONECTIVIDAD EXTERNA HTTPS
# ------------------------------------------------------------

$Internet = Test-TCPConnection `
    -HostName $Config.InternetTest.Host `
    -Port $Config.InternetTest.Port

$Resultados += [PSCustomObject]@{
    Categoria = "Internet HTTPS"
    Destino = $Config.InternetTest.Host
    Puerto = $Config.InternetTest.Port
    Estado = $Internet.Estado
    TiempoMs = $Internet.TiempoMs
}

# ------------------------------------------------------------
# 4. PRUEBAS DE PUERTOS TCP
# ------------------------------------------------------------

foreach ($Servicio in $Config.Ports) {

    $Prueba = Test-TCPConnection `
        -HostName $Servicio.Host `
        -Port $Servicio.Port

    $Resultados += [PSCustomObject]@{
        Categoria = $Servicio.Name
        Destino = $Servicio.Host
        Puerto = $Servicio.Port
        Estado = $Prueba.Estado
        TiempoMs = $Prueba.TiempoMs
    }
}

# ------------------------------------------------------------
# 5. RESULTADOS
# ------------------------------------------------------------

Write-Host "RESULTADOS DE CONECTIVIDAD" -ForegroundColor Cyan
Write-Host ""

if (-not $AsObject) {
    $Resultados | Format-Table -AutoSize -Wrap
}

$Disponibles = @($Resultados | Where-Object {
    $_.Estado -eq "DISPONIBLE"
}).Count

$NoDisponibles = @($Resultados | Where-Object {
    $_.Estado -eq "NO DISPONIBLE"
}).Count

Write-Host "RESUMEN DE CONECTIVIDAD" -ForegroundColor Cyan
Write-Host "Pruebas realizadas: $($Resultados.Count)"
Write-Host "Disponibles: $Disponibles"
Write-Host "No disponibles: $NoDisponibles"

Write-Host ""
Write-Host "Monitoreo de conectividad finalizado."


if ($AsObject) { $Resultados; return }
