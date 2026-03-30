from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


SUMMARY_COMMAND = r"""
$os = Get-CimInstance Win32_OperatingSystem | Select-Object -First 1
$cs = Get-CimInstance Win32_ComputerSystemProduct | Select-Object -First 1
$ci = Get-ComputerInfo
$cpuItems = @(Get-CimInstance Win32_Processor | ForEach-Object {
    @{
        name = $_.Name
        manufacturer = $_.Manufacturer
        cores = $_.NumberOfCores
        logical_cpus = $_.NumberOfLogicalProcessors
        max_clock_mhz = $_.MaxClockSpeed
        architecture = $_.Architecture
        socket = $_.SocketDesignation
    }
})
$memorySlots = @(Get-CimInstance Win32_PhysicalMemory | ForEach-Object {
    @{
        locator = $_.DeviceLocator
        capacity = $_.Capacity
        speed_mhz = $_.Speed
        manufacturer = $_.Manufacturer
        part_number = $_.PartNumber
        serial_number = $_.SerialNumber
        form_factor = $_.FormFactor
    }
})
$diskItems = @(Get-CimInstance Win32_DiskDrive | ForEach-Object {
    @{
        model = $_.Model
        size_bytes = $_.Size
        interface_type = $_.InterfaceType
        serial_number = $_.SerialNumber
        media_type = $_.MediaType
        partitions = $_.Partitions
    }
})
$gpuItems = @(Get-CimInstance Win32_VideoController | ForEach-Object {
    @{
        name = $_.Name
        driver_version = $_.DriverVersion
        video_memory_bytes = $_.AdapterRAM
        resolution = $_.VideoModeDescription
    }
} | Sort-Object name, driver_version -Unique)
$opticalDevices = @(Get-CimInstance Win32_CDROMDrive -ErrorAction SilentlyContinue | ForEach-Object { $_.Name })
$interfaces = @(Get-NetIPConfiguration | Where-Object { $_.NetAdapter } | ForEach-Object {
    $firstIp = if ($_.IPv4Address) { $_.IPv4Address | Select-Object -First 1 } else { $null }
    $dnsServers = @()
    if ($_.DNSServer.ServerAddresses) {
        $dnsServers = @($_.DNSServer.ServerAddresses | Where-Object { $_ })
    }
    @{
        name = $_.InterfaceDescription
        connection_name = $_.InterfaceAlias
        mac_address = $_.NetAdapter.MacAddress
        ipv4_address = if ($firstIp) { $firstIp.IPAddress } else { $null }
        subnet_mask = if ($firstIp) { $firstIp.PrefixLength } else { $null }
        default_gateway = if ($_.IPv4DefaultGateway) { $_.IPv4DefaultGateway.NextHop } else { $null }
        dns_servers = $dnsServers
        dhcp_enabled = $_.NetAdapter.DhcpEnabled
    }
})
$ipConfigs = @($interfaces | ForEach-Object {
    @{
        ip = $_.ipv4_address
        subnet_mask = $_.subnet_mask
        gateway = $_.default_gateway
        dns_servers = $_.dns_servers
        interface_alias = $_.connection_name
    }
})
@{
    summary = @{
        manufacturer = $cs.Vendor
        model_name = $cs.Name
        serial_number = $cs.IdentifyingNumber
        system_uuid = $cs.UUID
        cpu_model = if ($cpuItems.Count -gt 0) { $cpuItems[0].name } else { $null }
        cpu_items = $cpuItems
        memory_total = if ($os.TotalVisibleMemorySize) { [math]::Round($os.TotalVisibleMemorySize / 1024) } else { $null }
        memory_slots = $memorySlots
        disk_items = $diskItems
        gpu_items = $gpuItems
        storage_devices = @($diskItems | ForEach-Object { $_.model })
        display_devices = @($gpuItems | ForEach-Object { $_.name })
        optical_devices = $opticalDevices
        hostname = $env:COMPUTERNAME
        os_name = $os.Caption
        os_version = $os.Version
        os_build = $os.BuildNumber
        os_architecture = $os.OSArchitecture
        system_type = $ci.CsSystemType
        bios_version = $ci.BiosSMBIOSBIOSVersion
        domain = $ci.CsDomain
    }
    network = @{
        interfaces = $interfaces
        ip_addresses = $ipConfigs
        dns = @($interfaces | ForEach-Object { $_.dns_servers } | Where-Object { $_ })
        extra_addresses = @("127.0.0.1")
    }
}
"""


SOFTWARE_COMMAND = r"""
$paths = @(
    'HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*',
    'HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*'
)
$items = foreach ($path in $paths) {
    Get-ItemProperty $path -ErrorAction SilentlyContinue | Where-Object { $_.DisplayName } | ForEach-Object {
        @{
            name = $_.DisplayName
            version = $_.DisplayVersion
            vendor = $_.Publisher
            installed_on = if ($_.InstallDate) { [string]$_.InstallDate } else { $null }
        }
    }
}
@{ software = @($items | Sort-Object name, version, vendor) }
"""


PROCESS_COMMAND = r"""
$items = Get-Process | Sort-Object ProcessName, Id | ForEach-Object {
    @{
        name = $_.ProcessName
        pid = $_.Id
        session_name = $_.SessionId
        memory_kb = [int]($_.WorkingSet64 / 1KB)
    }
}
@{ processes = @($items) }
"""


ACCOUNTS_COMMAND = r"""
$items = Get-LocalUser -ErrorAction SilentlyContinue | Sort-Object Name | ForEach-Object {
    @{
        account_name = $_.Name
        enabled = $_.Enabled
        comment = $_.Description
    }
}
@{ accounts = @($items) }
"""


CONNECTION_COMMAND = r"""
$items = @()
$netstatLines = netstat -ano -n | Select-Object -Skip 4
foreach ($line in $netstatLines) {
    $trimmed = ($line -replace '\s+', ' ').Trim()
    if (-not $trimmed) { continue }
    $parts = $trimmed.Split(' ')
    if ($parts.Length -lt 4) { continue }

    if ($parts[0] -eq 'TCP' -and $parts.Length -ge 5) {
        $procId = 0
        [void][int]::TryParse($parts[4], [ref]$procId)
        $processName = $null
        if ($procId -gt 0) {
            try { $processName = (Get-Process -Id $procId -ErrorAction Stop).ProcessName } catch {}
        }
        $items += @{
            protocol = 'TCP'
            local_address = $parts[1]
            remote_address = $parts[2]
            state = $parts[3]
            process_name = $processName
        }
        continue
    }

    if ($parts[0] -eq 'UDP' -and $parts.Length -ge 4) {
        $procId = 0
        [void][int]::TryParse($parts[3], [ref]$procId)
        $processName = $null
        if ($procId -gt 0) {
            try { $processName = (Get-Process -Id $procId -ErrorAction Stop).ProcessName } catch {}
        }
        $items += @{
            protocol = 'UDP'
            local_address = $parts[1]
            remote_address = $parts[2]
            state = $null
            process_name = $processName
        }
    }
}
@{ network = @{ connections = @($items) } }
"""


HOTFIX_COMMAND = r"""
$items = Get-HotFix -ErrorAction SilentlyContinue | Sort-Object HotFixID | ForEach-Object {
    @{
        hotfix_id = $_.HotFixID
        description = $_.Description
        installed_on = $_.InstalledOn
        installed_by = $_.InstalledBy
    }
}
@{ hotfixes = @($items) }
"""


DEFAULT_COLLECT_SCRIPTS = [
    {
        "script_key": "summary",
        "display_name": "\uc591\uc2dd1 - \uae30\ubcf8 \uc694\uc57d",
        "description": "\uc2dc\uc2a4\ud15c, \uba54\ubaa8\ub9ac, \ub514\uc2a4\ud06c, GPU, NIC/IP, OS \uc815\ubcf4\ub97c \uc218\uc9d1\ud569\ub2c8\ub2e4.",
        "ps_command": SUMMARY_COMMAND,
        "ps_filename": "collect_summary.ps1",
        "target_table": "asset_hw_systems",
        "output_format": "json",
        "sort_order": 10,
    },
    {
        "script_key": "software",
        "display_name": "\uc591\uc2dd2 - \uc124\uce58 \ud504\ub85c\uadf8\ub7a8",
        "description": "\uc124\uce58\ub41c \ud504\ub85c\uadf8\ub7a8 \uc804\uccb4 \ubaa9\ub85d\uc744 \uc218\uc9d1\ud569\ub2c8\ub2e4.",
        "ps_command": SOFTWARE_COMMAND,
        "ps_filename": "collect_software.ps1",
        "target_table": "asset_sw_products",
        "output_format": "json",
        "sort_order": 20,
    },
    {
        "script_key": "processes",
        "display_name": "\uc591\uc2dd3 - \uc2e4\ud589 \ud504\ub85c\uc138\uc2a4",
        "description": "\uc2e4\ud589 \uc911\uc778 \ud504\ub85c\uc138\uc2a4 \ubaa9\ub85d\uc744 \uc218\uc9d1\ud569\ub2c8\ub2e4.",
        "ps_command": PROCESS_COMMAND,
        "ps_filename": "collect_processes.ps1",
        "target_table": "asset_sw_processes",
        "output_format": "json",
        "sort_order": 30,
    },
    {
        "script_key": "accounts",
        "display_name": "\uc591\uc2dd3-1 - \ub85c\uceec \uacc4\uc815",
        "description": "Get-LocalUser \uae30\ubc18 \ub85c\uceec \uacc4\uc815, \ud65c\uc131\ud654, \uc8fc\uc11d \uc815\ubcf4\ub97c \uc218\uc9d1\ud569\ub2c8\ub2e4.",
        "ps_command": ACCOUNTS_COMMAND,
        "ps_filename": "collect_accounts.ps1",
        "target_table": "asset_sw_accounts",
        "output_format": "json",
        "sort_order": 35,
    },
    {
        "script_key": "network_connections",
        "display_name": "\uc591\uc2dd4 - \ub124\ud2b8\uc6cc\ud06c \uc5f0\uacb0",
        "description": "netstat \uae30\ubc18 \ub124\ud2b8\uc6cc\ud06c \uc5f0\uacb0 \uc815\ubcf4\ub97c \uc218\uc9d1\ud569\ub2c8\ub2e4.",
        "ps_command": CONNECTION_COMMAND,
        "ps_filename": "collect_network_connections.ps1",
        "target_table": "asset_network_connections",
        "output_format": "json",
        "sort_order": 40,
    },
    {
        "script_key": "hotfixes",
        "display_name": "\uc591\uc2dd5 - Windows \uc5c5\ub370\uc774\ud2b8",
        "description": "\uc124\uce58\ub41c Hotfix/KB \ubaa9\ub85d\uc744 \uc218\uc9d1\ud569\ub2c8\ub2e4.",
        "ps_command": HOTFIX_COMMAND,
        "ps_filename": "collect_hotfixes.ps1",
        "target_table": "asset_sw_hotfixes",
        "output_format": "json",
        "sort_order": 50,
    },
]


async def ensure_default_collect_scripts(session: AsyncSession) -> None:
    for script in DEFAULT_COLLECT_SCRIPTS:
        await session.execute(
            text(
                """
                INSERT INTO collect_scripts (
                    script_key, display_name, description, ps_command, ps_filename,
                    target_table, output_format, is_active, sort_order
                ) VALUES (
                    :script_key, :display_name, :description, :ps_command, :ps_filename,
                    :target_table, :output_format, true, :sort_order
                )
                ON CONFLICT (script_key) DO UPDATE SET
                    display_name = EXCLUDED.display_name,
                    description = EXCLUDED.description,
                    ps_command = EXCLUDED.ps_command,
                    ps_filename = EXCLUDED.ps_filename,
                    target_table = EXCLUDED.target_table,
                    output_format = EXCLUDED.output_format,
                    sort_order = EXCLUDED.sort_order,
                    updated_at = NOW()
                """
            ),
            script,
        )
    await session.commit()
