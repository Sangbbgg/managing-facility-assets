import tempfile
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collect_script import CollectScript


def _script_header_lines(title: str) -> list[str]:
    return [
        "#Requires -Version 5.1",
        f"# {title}",
        f"# generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "param(",
        '    [string]$AssetCode = ""',
        ")",
        "",
        '$ErrorActionPreference = "SilentlyContinue"',
        "",
        "$result = @{",
        "    meta = @{",
        "        asset_code = $AssetCode",
        "        hostname = $env:COMPUTERNAME",
        '        collected_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")',
        '        collector_version = "v1"',
        '        source = "powershell"',
        "    }",
        "}",
        "",
    ]


def _merge_fragment_lines(fragment_expr: str) -> list[str]:
    expr_lines = [line.rstrip() for line in fragment_expr.strip().splitlines()]
    return [
        "$fragment = & {",
        *[f"    {line}" if line else "" for line in expr_lines],
        "}",
        "if ($fragment) {",
        "    foreach ($key in $fragment.Keys) {",
        "        if ($fragment[$key] -is [hashtable] -and $result[$key] -is [hashtable]) {",
        "            foreach ($subKey in $fragment[$key].Keys) {",
        "                $result[$key][$subKey] = $fragment[$key][$subKey]",
        "            }",
        "        } else {",
        "            $result[$key] = $fragment[$key]",
        "        }",
        "    }",
        "}",
        "",
    ]


def _script_footer_lines(default_filename: str) -> list[str]:
    return [
        f'$filename = "{default_filename}"',
        "$result | ConvertTo-Json -Depth 8 | Out-File -FilePath $filename -Encoding UTF8",
        'Write-Host ""',
        'Write-Host "=== Collection Complete ===" -ForegroundColor Green',
        'Write-Host ("File: {0}" -f (Get-Item $filename).FullName) -ForegroundColor Green',
    ]


async def generate_bundle_script(db: AsyncSession) -> str:
    result = await db.execute(
        select(CollectScript).where(CollectScript.is_active == True).order_by(CollectScript.sort_order)
    )
    scripts = result.scalars().all()

    lines = _script_header_lines("Asset Collection Bundle")

    for index, script in enumerate(scripts, 1):
        lines.append(f"# [{index}/{len(scripts)}] {script.display_name}")
        if script.description:
            lines.append(f"# {script.description}")
        lines.append(f'Write-Host "[{index}/{len(scripts)}] {script.display_name} collecting..." -ForegroundColor Yellow')
        lines.append("try {")
        lines.extend([f"    {line}" if line else "" for line in _merge_fragment_lines(script.ps_command)])
        lines.append("} catch {")
        lines.append(f'    Write-Host "  Warning: {script.display_name} collection failed - $_" -ForegroundColor Red')
        lines.append("}")
        lines.append("")

    lines.extend(_script_footer_lines("asset_collect_bundle.json"))
    return _write_temp_ps1(lines)


async def generate_single_script(db: AsyncSession, script_key: str) -> str:
    script = await db.scalar(select(CollectScript).where(CollectScript.script_key == script_key))
    if not script:
        raise ValueError(f"Script not found: {script_key}")

    filename = script.ps_filename or f"collect_{script_key}.ps1"
    output_name = filename.replace(".ps1", ".json")

    lines = _script_header_lines(script.display_name)
    if script.description:
        lines.append(f"# {script.description}")
        lines.append("")
    lines.extend(_merge_fragment_lines(script.ps_command))
    lines.extend(_script_footer_lines(output_name))
    return _write_temp_ps1(lines)


def _write_temp_ps1(lines: list[str]) -> str:
    tmp = tempfile.NamedTemporaryFile(suffix=".ps1", delete=False, mode="w", encoding="utf-8-sig")
    tmp.write("\n".join(lines))
    tmp.close()
    return tmp.name
