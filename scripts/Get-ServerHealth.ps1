# ============================================================
# ServerHealth Monitor
# Version: 1.0
# Compatibility: Windows PowerShell 5.1
# Module: CPU, RAM and Disk Monitoring
# ============================================================

param([switch]$AsObject)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "         SERVER HEALTH MONITOR            " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

$Resultados = @()

# ------------------------------------------------------------
# 1. CPU
# ------------------------------------------------------------

try {
    $CPU = Get-CimInstance Win32_PerfFormattedData_PerfOS_Processor `
        -Filter "Name='_Total'"

    if ($null -eq $CPU) {
        throw "No fue posible obtener el consumo de CPU."
    }

    $UsoCPU = [math]::Round($CPU.PercentProcessorTime, 2)

    $EstadoCPU = if ($UsoCPU -ge 95) {
        "CRITICO"
    }
    elseif ($UsoCPU -ge 85) {
        "ADVERTENCIA"
    }
    else {
        "OK"
    }

    $Resultados += [PSCustomObject]@{
        Recurso = "CPU"
        Valor = "$UsoCPU %"
        Estado = $EstadoCPU
    }
}
catch {
    $Resultados += [PSCustomObject]@{
        Recurso = "CPU"
        Valor = "No disponible"
        Estado = "ERROR"
    }
}

# ------------------------------------------------------------
# 2. MEMORIA RAM
# ------------------------------------------------------------

try {
    $SO = Get-CimInstance Win32_OperatingSystem

    $RAMTotal = [double]$SO.TotalVisibleMemorySize
    $RAMLibre = [double]$SO.FreePhysicalMemory

    if ($RAMTotal -le 0) {
        throw "Capacidad de memoria no válida."
    }

    $RAMUsada = $RAMTotal - $RAMLibre
    $PorcentajeRAM = [math]::Round(
        ($RAMUsada / $RAMTotal) * 100, 2
    )

    $RAMTotalGB = [math]::Round($RAMTotal / 1MB, 2)
    $RAMLibreGB = [math]::Round($RAMLibre / 1MB, 2)

    $EstadoRAM = if ($PorcentajeRAM -ge 95) {
        "CRITICO"
    }
    elseif ($PorcentajeRAM -ge 85) {
        "ADVERTENCIA"
    }
    else {
        "OK"
    }

    $Resultados += [PSCustomObject]@{
        Recurso = "RAM"
        Valor = "$PorcentajeRAM % utilizada ($RAMLibreGB GB libres de $RAMTotalGB GB)"
        Estado = $EstadoRAM
    }
}
catch {
    $Resultados += [PSCustomObject]@{
        Recurso = "RAM"
        Valor = "No disponible"
        Estado = "ERROR"
    }
}

# ------------------------------------------------------------
# 3. DISCOS LOCALES
# ------------------------------------------------------------

try {
    $Discos = Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3"

    foreach ($Disco in $Discos) {

        if ($Disco.Size -le 0) {
            continue
        }

        $LibreGB = [math]::Round($Disco.FreeSpace / 1GB, 2)
        $TotalGB = [math]::Round($Disco.Size / 1GB, 2)

        $PorcentajeLibre = [math]::Round(
            ($Disco.FreeSpace / $Disco.Size) * 100, 2
        )

        $EstadoDisco = if ($PorcentajeLibre -le 5) {
            "CRITICO"
        }
        elseif ($PorcentajeLibre -le 15) {
            "ADVERTENCIA"
        }
        else {
            "OK"
        }

        $Resultados += [PSCustomObject]@{
            Recurso = "Disco $($Disco.DeviceID)"
            Valor = "$PorcentajeLibre % libre ($LibreGB GB de $TotalGB GB)"
            Estado = $EstadoDisco
        }
    }
}
catch {
    $Resultados += [PSCustomObject]@{
        Recurso = "DISCOS"
        Valor = "No disponibles"
        Estado = "ERROR"
    }
}

# ------------------------------------------------------------
# 4. RESULTADO
# ------------------------------------------------------------

Write-Host "EQUIPO: $env:COMPUTERNAME" -ForegroundColor Yellow
Write-Host "FECHA: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
Write-Host ""

if (-not $AsObject) {
    $Resultados | Format-Table -AutoSize -Wrap
}

$Criticos = @($Resultados | Where-Object {
    $_.Estado -eq "CRITICO"
}).Count

$Advertencias = @($Resultados | Where-Object {
    $_.Estado -eq "ADVERTENCIA"
}).Count

$Errores = @($Resultados | Where-Object {
    $_.Estado -eq "ERROR"
}).Count

Write-Host "RESUMEN DEL MONITOREO" -ForegroundColor Cyan
Write-Host "Recursos revisados: $($Resultados.Count)"
Write-Host "Criticos: $Criticos"
Write-Host "Advertencias: $Advertencias"
Write-Host "Errores: $Errores"

if ($Criticos -gt 0 -or $Errores -gt 0) {
    Write-Host "`nRESULTADO GENERAL: REQUIERE ATENCION" -ForegroundColor Red
}
elseif ($Advertencias -gt 0) {
    Write-Host "`nRESULTADO GENERAL: ADVERTENCIA" -ForegroundColor Yellow
}
else {
    Write-Host "`nRESULTADO GENERAL: NORMAL" -ForegroundColor Green
}

Write-Host ""
Write-Host "Monitoreo finalizado."


if ($AsObject) { $Resultados; return }
