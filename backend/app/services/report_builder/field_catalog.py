"""
data_source 별 사용 가능한 전체 필드 목록.
"""

_ASSET_COMMON = [
    {"field": "asset_code", "label": "자산코드", "width": 18},
    {"field": "asset_name", "label": "설비명", "width": 20},
    {"field": "ip_address", "label": "IP 주소", "width": 16},
    {"field": "purpose", "label": "용도", "width": 20},
    {"field": "importance", "label": "중요도", "width": 8},
    {"field": "status", "label": "상태", "width": 10},
    {"field": "install_date", "label": "설치일", "width": 12},
    {"field": "created_at", "label": "등록일", "width": 14},
    {"field": "updated_at", "label": "최종수정일", "width": 14},
    {"field": "last_collected_at", "label": "최종수집일", "width": 14},
    {"field": "group_name", "label": "그룹명", "width": 20},
    {"field": "group_full_path", "label": "그룹 경로", "width": 30},
    {"field": "group_code", "label": "그룹코드", "width": 12},
    {"field": "location_name", "label": "위치명", "width": 16},
    {"field": "location_full_path", "label": "위치 경로", "width": 30},
    {"field": "equipment_type_name", "label": "장비종류", "width": 14},
    {"field": "equipment_type_code", "label": "장비코드", "width": 12},
    {"field": "manager_name", "label": "담당자", "width": 12},
    {"field": "manager_title", "label": "담당자직급", "width": 10},
    {"field": "manager_contact", "label": "담당자연락처", "width": 18},
]

_ASSET_BASE = [
    {"field": "asset_code", "label": "자산코드", "width": 18},
    {"field": "asset_name", "label": "설비명", "width": 20},
    {"field": "group_name", "label": "그룹명", "width": 20},
    {"field": "location_full_path", "label": "위치", "width": 30},
    {"field": "ip_address", "label": "IP 주소", "width": 16},
]

FIELD_CATALOG: dict[str, list[dict]] = {
    "정상관리대장": _ASSET_COMMON,
    "설비관리대장": _ASSET_COMMON,
    "점검대장_월간": _ASSET_BASE + [
        {"field": "record_date", "label": "점검일", "width": 12},
        {"field": "inspection_type", "label": "점검유형", "width": 10},
        {"field": "result", "label": "결과", "width": 8},
        {"field": "inspector", "label": "점검자", "width": 12},
        {"field": "special_notes", "label": "특이사항", "width": 30},
    ],
    "점검대장_분기": _ASSET_BASE + [
        {"field": "record_date", "label": "점검일", "width": 12},
        {"field": "inspection_type", "label": "점검유형", "width": 10},
        {"field": "result", "label": "결과", "width": 8},
        {"field": "inspector", "label": "점검자", "width": 12},
        {"field": "special_notes", "label": "특이사항", "width": 30},
    ],
    "이벤트로그": _ASSET_BASE + [
        {"field": "record_date", "label": "날짜", "width": 12},
        {"field": "log_type", "label": "로그유형", "width": 10},
        {"field": "event_id", "label": "이벤트ID", "width": 12},
        {"field": "level", "label": "레벨", "width": 10},
        {"field": "count", "label": "건수", "width": 8},
    ],
    "콘솔접속대장": _ASSET_BASE + [
        {"field": "access_date", "label": "접속일", "width": 12},
        {"field": "accessor", "label": "접속자", "width": 14},
        {"field": "purpose", "label": "목적", "width": 30},
    ],
    "봉인지관리대장": _ASSET_BASE + [
        {"field": "record_date", "label": "봉인지일", "width": 12},
        {"field": "seal_number", "label": "봉인지번호", "width": 16},
        {"field": "action", "label": "구분", "width": 10},
        {"field": "handler", "label": "담당자", "width": 12},
        {"field": "notes", "label": "비고", "width": 30},
    ],
    "비밀번호관리대장": _ASSET_BASE + [
        {"field": "account_name", "label": "계정명", "width": 20},
        {"field": "changed_date", "label": "변경일", "width": 12},
        {"field": "changed_by", "label": "변경자", "width": 14},
        {"field": "notes", "label": "비고", "width": 30},
    ],
}

DATA_SOURCES = list(FIELD_CATALOG.keys())
MULTI_SHEET_SOURCES = {"점검대장_월간", "점검대장_분기", "이벤트로그"}
