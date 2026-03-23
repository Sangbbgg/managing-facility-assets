from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.core.database import engine, AsyncSessionLocal
from app.models import Base  # noqa: F401 — 모든 모델 등록
from app.api.routes import (
    health, locations, groups, assets, catalogs, persons, reports, evtx,
    layouts, hardware, software, custom_fields, collect,
)

_COLLECT_SCRIPTS_SEED = [
    {
        "script_key": "system",
        "display_name": "시스템 종합 정보",
        "description": "제조사, 모델명, S/N, OS 정보, BIOS, 총 메모리 등을 수집합니다.",
        "legacy_command": "wmic csproduct + wmic os + systeminfo /fo csv",
        "ps_command": (
            "@{ csproduct = Get-CimInstance Win32_ComputerSystemProduct | Select-Object *; "
            "os = Get-CimInstance Win32_OperatingSystem | Select-Object *; "
            "computerinfo = Get-ComputerInfo | Select-Object * }"
        ),
        "ps_filename": "collect_system.ps1",
        "target_table": "asset_hw_systems",
        "sort_order": 1,
    },
    {
        "script_key": "cpu",
        "display_name": "CPU 정보",
        "description": "프로세서 모델, 코어 수, 클럭 속도, 아키텍처 등을 수집합니다.",
        "legacy_command": "wmic cpu get /format:csv",
        "ps_command": (
            "@(Get-CimInstance Win32_Processor | "
            "Select-Object Name,Manufacturer,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed,Architecture,SocketDesignation)"
        ),
        "ps_filename": "collect_cpu.ps1",
        "target_table": "asset_hw_cpus",
        "sort_order": 2,
    },
    {
        "script_key": "memory",
        "display_name": "메모리 정보",
        "description": "각 DIMM 슬롯의 용량, 속도, 제조사, S/N 등을 수집합니다.",
        "legacy_command": "wmic memorychip get /format:csv",
        "ps_command": (
            "@(Get-CimInstance Win32_PhysicalMemory | "
            "Select-Object DeviceLocator,Capacity,Speed,Manufacturer,SerialNumber,FormFactor)"
        ),
        "ps_filename": "collect_memory.ps1",
        "target_table": "asset_hw_memories",
        "sort_order": 3,
    },
    {
        "script_key": "disk",
        "display_name": "디스크 정보",
        "description": "디스크 모델, 용량, 인터페이스 타입, S/N 등을 수집합니다.",
        "legacy_command": "wmic diskdrive get /format:csv",
        "ps_command": (
            "@(Get-CimInstance Win32_DiskDrive | "
            "Select-Object Model,Size,InterfaceType,SerialNumber,MediaType,Partitions)"
        ),
        "ps_filename": "collect_disk.ps1",
        "target_table": "asset_hw_disks",
        "sort_order": 4,
    },
    {
        "script_key": "gpu",
        "display_name": "GPU/디스플레이 정보",
        "description": "GPU 모델, 드라이버 버전, 비디오 메모리 등을 수집합니다.",
        "legacy_command": "dxdiag /t",
        "ps_command": (
            "@(Get-CimInstance Win32_VideoController | "
            "Select-Object Name,DriverVersion,AdapterRAM,VideoModeDescription)"
        ),
        "ps_filename": "collect_gpu.ps1",
        "target_table": "asset_hw_gpus",
        "sort_order": 5,
    },
    {
        "script_key": "nic",
        "display_name": "네트워크 어댑터 정보",
        "description": "NIC 이름, MAC 주소, IP, 서브넷, 게이트웨이, DHCP 여부 등을 수집합니다.",
        "legacy_command": "ipconfig /all",
        "ps_command": (
            "@(Get-NetIPConfiguration | "
            "Select-Object InterfaceAlias,InterfaceDescription,IPv4Address,IPv4DefaultGateway,DNSServer)"
        ),
        "ps_filename": "collect_nic.ps1",
        "target_table": "asset_hw_nics",
        "sort_order": 6,
    },
    {
        "script_key": "product",
        "display_name": "설치 프로그램 목록",
        "description": "설치된 소프트웨어 이름, 버전, 제조사, 설치일을 수집합니다.",
        "legacy_command": "wmic product get /format:csv",
        "ps_command": (
            "@(Get-CimInstance Win32_Product | "
            "Select-Object Name,Version,Vendor,InstallDate)"
        ),
        "ps_filename": "collect_product.ps1",
        "target_table": "asset_sw_products",
        "sort_order": 7,
    },
    {
        "script_key": "hotfix",
        "display_name": "핫픽스/패치 목록",
        "description": "설치된 Windows 업데이트 KB번호, 설명, 설치일을 수집합니다.",
        "legacy_command": "wmic qfe get /format:csv",
        "ps_command": (
            "@(Get-HotFix | "
            "Select-Object HotFixID,Description,InstalledOn,InstalledBy)"
        ),
        "ps_filename": "collect_hotfix.ps1",
        "target_table": "asset_sw_hotfixes",
        "sort_order": 8,
    },
    {
        "script_key": "process",
        "display_name": "실행 프로세스 스냅샷",
        "description": "현재 실행 중인 프로세스 이름, PID, 메모리 사용량을 수집합니다.",
        "legacy_command": "tasklist /fo csv",
        "ps_command": (
            "@(Get-Process | "
            "Select-Object ProcessName,Id,SessionId,@{N='WorkingSetKB';E={[math]::Round($_.WorkingSet64/1KB)}})"
        ),
        "ps_filename": "collect_process.ps1",
        "target_table": "asset_sw_processes",
        "sort_order": 9,
    },
]


_DEFAULT_TEMPLATES = [
    {
        "name": "형상관리대장", "display_name": "형상관리대장",
        "data_source": "형상관리대장", "sheet_name": "형상관리대장", "header_color": "#1F4E79",
        "columns": [
            {"header": "자산코드",  "field": "asset_code",          "width": 18},
            {"header": "설비명",    "field": "asset_name",          "width": 20},
            {"header": "그룹",      "field": "group_name",          "width": 20},
            {"header": "위치",      "field": "location_full_path",  "width": 20},
            {"header": "장비종류",  "field": "equipment_type_name", "width": 12},
            {"header": "OS",        "field": "os_name",             "width": 22},
            {"header": "백신",      "field": "av_name",             "width": 22},
            {"header": "IP",        "field": "ip_address",          "width": 16},
            {"header": "시리얼",    "field": "serial_number",       "width": 18},
            {"header": "중요도",    "field": "importance",          "width": 8},
            {"header": "설치일",    "field": "install_date",        "width": 12},
            {"header": "상태",      "field": "status",              "width": 10},
        ],
    },
    {
        "name": "설비관리대장", "display_name": "설비관리대장",
        "data_source": "설비관리대장", "sheet_name": "설비관리대장", "header_color": "#1F4E79",
        "columns": [
            {"header": "자산코드", "field": "asset_code",     "width": 18},
            {"header": "설비명",   "field": "asset_name",     "width": 20},
            {"header": "담당자",   "field": "manager_name",   "width": 12},
            {"header": "직책",     "field": "manager_title",  "width": 10},
            {"header": "부서",     "field": "manager_dept",   "width": 16},
            {"header": "연락처",   "field": "manager_contact","width": 18},
            {"header": "책임자",   "field": "supervisor_name","width": 12},
            {"header": "상태",     "field": "status",         "width": 10},
        ],
    },
    {
        "name": "예방점검_월간", "display_name": "예방점검 월간보고서",
        "data_source": "예방점검_월간", "sheet_name": "예방점검_월간", "header_color": "#1F4E79",
        "columns": [
            {"header": "자산코드", "field": "asset_code",     "width": 18},
            {"header": "설비명",   "field": "asset_name",     "width": 20},
            {"header": "점검일",   "field": "record_date",    "width": 12},
            {"header": "점검유형", "field": "inspection_type","width": 10},
            {"header": "결과",     "field": "result",         "width": 8},
            {"header": "점검자",   "field": "inspector",      "width": 12},
            {"header": "특이사항", "field": "special_notes",  "width": 30},
        ],
    },
    {
        "name": "예방점검_분기", "display_name": "예방점검 분기보고서",
        "data_source": "예방점검_분기", "sheet_name": "예방점검_분기", "header_color": "#1F4E79",
        "columns": [
            {"header": "자산코드", "field": "asset_code",     "width": 18},
            {"header": "설비명",   "field": "asset_name",     "width": 20},
            {"header": "점검일",   "field": "record_date",    "width": 12},
            {"header": "점검유형", "field": "inspection_type","width": 10},
            {"header": "결과",     "field": "result",         "width": 8},
            {"header": "점검자",   "field": "inspector",      "width": 12},
            {"header": "특이사항", "field": "special_notes",  "width": 30},
        ],
    },
    {
        "name": "이벤트로그", "display_name": "이벤트로그",
        "data_source": "이벤트로그", "sheet_name": "이벤트로그", "header_color": "#1F4E79",
        "columns": [
            {"header": "자산코드",  "field": "asset_code",  "width": 18},
            {"header": "설비명",    "field": "asset_name",  "width": 20},
            {"header": "날짜",      "field": "record_date", "width": 12},
            {"header": "로그유형",  "field": "log_type",    "width": 10},
            {"header": "이벤트ID",  "field": "event_id",    "width": 12},
            {"header": "레벨",      "field": "level",       "width": 10},
            {"header": "건수",      "field": "count",       "width": 8},
        ],
    },
    {
        "name": "콘솔접속대장", "display_name": "콘솔접속대장",
        "data_source": "콘솔접속대장", "sheet_name": "콘솔접속대장", "header_color": "#1F4E79",
        "columns": [
            {"header": "자산코드", "field": "asset_code", "width": 18},
            {"header": "설비명",   "field": "asset_name", "width": 20},
            {"header": "접속일",   "field": "access_date","width": 12},
            {"header": "접속자",   "field": "accessor",   "width": 14},
            {"header": "목적",     "field": "purpose",    "width": 30},
        ],
    },
    {
        "name": "봉인지관리대장", "display_name": "봉인지관리대장",
        "data_source": "봉인지관리대장", "sheet_name": "봉인지관리대장", "header_color": "#1F4E79",
        "columns": [
            {"header": "자산코드", "field": "asset_code",  "width": 18},
            {"header": "설비명",   "field": "asset_name",  "width": 20},
            {"header": "봉인일",   "field": "record_date", "width": 12},
            {"header": "봉인번호", "field": "seal_number", "width": 16},
            {"header": "구분",     "field": "action",      "width": 10},
            {"header": "담당자",   "field": "handler",     "width": 12},
            {"header": "비고",     "field": "notes",       "width": 30},
        ],
    },
    {
        "name": "비밀번호관리대장", "display_name": "비밀번호관리대장",
        "data_source": "비밀번호관리대장", "sheet_name": "비밀번호관리대장", "header_color": "#1F4E79",
        "columns": [
            {"header": "자산코드", "field": "asset_code",   "width": 18},
            {"header": "설비명",   "field": "asset_name",   "width": 20},
            {"header": "계정명",   "field": "account_name", "width": 20},
            {"header": "변경일",   "field": "changed_date", "width": 12},
            {"header": "변경자",   "field": "changed_by",   "width": 14},
            {"header": "비고",     "field": "notes",        "width": 30},
        ],
    },
]


async def _seed_report_templates():
    """report_templates 테이블이 비어있으면 기본 8개 서식 삽입"""
    from app.models.report import ReportTemplate
    async with AsyncSessionLocal() as session:
        count = await session.scalar(select(ReportTemplate).limit(1))
        if count is not None:
            return
        for tmpl in _DEFAULT_TEMPLATES:
            session.add(ReportTemplate(**tmpl))
        await session.commit()


async def _seed_collect_scripts():
    """collect_scripts 테이블이 비어있으면 초기 9건 삽입"""
    from app.models.collect_script import CollectScript
    async with AsyncSessionLocal() as session:
        count = await session.scalar(
            select(CollectScript).limit(1)
        )
        if count is not None:
            return  # 이미 데이터 있음
        for row in _COLLECT_SCRIPTS_SEED:
            session.add(CollectScript(**row))
        await session.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await _seed_report_templates()
    await _seed_collect_scripts()
    yield
    await engine.dispose()


app = FastAPI(title="설비관리 시스템 API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router,        prefix="/api")
app.include_router(locations.router,     prefix="/api/locations",      tags=["locations"])
app.include_router(groups.router,        prefix="/api/groups",         tags=["groups"])
app.include_router(assets.router,        prefix="/api/assets",         tags=["assets"])
app.include_router(catalogs.router,      prefix="/api/catalogs",       tags=["catalogs"])
app.include_router(persons.router,       prefix="/api/persons",        tags=["persons"])
app.include_router(reports.router,       prefix="/api/reports",        tags=["reports"])
app.include_router(evtx.router,          prefix="/api/evtx",           tags=["evtx"])
# v2 신규 라우터
app.include_router(layouts.router,       prefix="/api/layouts",        tags=["layouts"])
app.include_router(hardware.router,      prefix="/api/assets",         tags=["hardware"])
app.include_router(software.router,      prefix="/api/assets",         tags=["software"])
app.include_router(custom_fields.router, prefix="/api/assets",         tags=["custom-fields"])
app.include_router(collect.router,       prefix="/api/collect",        tags=["collect"])
