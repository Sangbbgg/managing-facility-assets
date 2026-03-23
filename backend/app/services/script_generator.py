import tempfile
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.collect_script import CollectScript


async def generate_bundle_script(db: AsyncSession) -> str:
    result = await db.execute(
        select(CollectScript)
        .where(CollectScript.is_active == True)
        .order_by(CollectScript.sort_order)
    )
    scripts = result.scalars().all()
    total = len(scripts)

    lines = [
        '#Requires -Version 5.1',
        f'# 설비관리 시스템 — 자산 정보 수집 스크립트 (자동생성: {datetime.now().strftime("%Y-%m-%d %H:%M")})',
        '# 실행 후 생성된 JSON 파일을 [자산 세부사항 → 수집 업로드] 탭에서 업로드하세요.',
        '',
        '$ErrorActionPreference = "SilentlyContinue"',
        '',
        '$result = @{',
        '    _meta = @{',
        '        collected_at = (Get-Date -Format "yyyy-MM-ddTHH:mm:sszzz")',
        '        hostname     = $env:COMPUTERNAME',
        '        script_ver   = "2.0"',
        '    }',
        '}',
        '',
    ]

    for idx, script in enumerate(scripts, 1):
        lines.append(f'# [{idx}/{total}] {script.display_name}')
        if script.description:
            lines.append(f'# {script.description}')
        lines.append(f'Write-Host "[{idx}/{total}] {script.display_name} 수집 중..." -ForegroundColor Yellow')
        lines.append(f'try {{')
        lines.append(f'    $result.{script.script_key} = {script.ps_command}')
        lines.append(f'}} catch {{ Write-Host "  경고: {script.display_name} 수집 실패 - $_" -ForegroundColor Red }}')
        lines.append('')

    lines.extend([
        '# JSON 저장',
        '$filename = "asset_collect_{0}_{1}.json" -f $env:COMPUTERNAME, (Get-Date -Format "yyyyMMdd_HHmmss")',
        '$result | ConvertTo-Json -Depth 5 | Out-File -FilePath $filename -Encoding UTF8',
        'Write-Host ""',
        'Write-Host "=== 수집 완료 ===" -ForegroundColor Green',
        'Write-Host "파일: $((Get-Item $filename).FullName)" -ForegroundColor Green',
    ])

    tmp = tempfile.NamedTemporaryFile(
        suffix=".ps1", delete=False, mode='w', encoding='utf-8-sig'
    )
    tmp.write('\n'.join(lines))
    tmp.close()
    return tmp.name


async def generate_single_script(db: AsyncSession, script_key: str) -> str:
    script = await db.scalar(
        select(CollectScript).where(CollectScript.script_key == script_key)
    )
    if not script:
        raise ValueError(f"스크립트를 찾을 수 없습니다: {script_key}")

    lines = [
        '#Requires -Version 5.1',
        f'# {script.display_name} 수집 스크립트',
        f'# {script.description or ""}',
        f'# 대상 테이블: {script.target_table}',
        '',
        '$ErrorActionPreference = "SilentlyContinue"',
        f'$data = {script.ps_command}',
        '$data | ConvertTo-Json -Depth 5',
    ]

    tmp = tempfile.NamedTemporaryFile(
        suffix=".ps1", delete=False, mode='w', encoding='utf-8-sig'
    )
    tmp.write('\n'.join(lines))
    tmp.close()
    return tmp.name
