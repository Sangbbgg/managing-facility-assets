# 설비관리 시스템 — 구현 스냅샷

> 작성일: 2026-03-23
> 브랜치: `claude/condescending-mendel`
> 최신 커밋: `be94426`

---

## 1. 스택 & 인프라

| 영역 | 기술 | 비고 |
|------|------|------|
| 프론트엔드 | Vue 3 + Vite 5 | Naive UI 2.x, Pinia 2.x, Axios 1.x |
| 백엔드 | FastAPI + Python 3.12 | SQLAlchemy async 2.x |
| DB | PostgreSQL 16 | asyncpg 드라이버 |
| 보고서 | openpyxl 3.x | 동적 템플릿 시스템 |
| evtx | python-evtx + lxml + ProcessPoolExecutor | - |
| 배포 | Docker Compose v2 | Nginx 리버스 프록시 |

**포트 구성**
- `:80` — Nginx (프론트엔드 + `/api/` 프록시)
- `:8000` — FastAPI 백엔드 (직접 접근 시 CORS 차단)
- `:5432` — PostgreSQL

---

## 2. DB 테이블 현황 (27개)

### 기존 15개 (Phase 0~7)

| 파일 | 테이블 | 설명 |
|------|--------|------|
| `master.py` | `location_nodes` | 위치 트리 |
| | `group_nodes` | 그룹 트리 (code 있는 노드만 자산 등록 가능) |
| | `equipment_types` | 장비 종류 카탈로그 |
| | `os_catalog` | OS 카탈로그 (EoL 날짜 포함) |
| | `antivirus_catalog` | 백신 카탈로그 |
| | `departments` | 부서 |
| | `persons` | 담당자 |
| `asset.py` | `assets` | 자산 (자산코드, 상태, last_collected_at 등) |
| | `asset_code_sequences` | 자산코드 채번 (SELECT FOR UPDATE) |
| | `asset_change_log` | 자산 변경 이력 |
| `record.py` | `inspection_records` | 예방점검 이력 |
| | `event_log_records` | 이벤트로그 이력 |
| | `console_access_records` | 콘솔접속 이력 |
| | `seal_records` | 봉인지 이력 |
| | `password_records` | 비밀번호 변경 이력 |

### V2 신규 12개 (Phase 8~14)

| 파일 | 테이블 | 설명 |
|------|--------|------|
| `hw_info.py` | `asset_hw_systems` | HW 시스템 정보 (제조사/모델/S/N/OS) |
| | `asset_hw_cpus` | CPU 정보 |
| | `asset_hw_memories` | 메모리 슬롯별 정보 |
| | `asset_hw_disks` | 디스크 정보 |
| | `asset_hw_gpus` | GPU 정보 |
| | `asset_hw_nics` | NIC/네트워크 어댑터 정보 |
| `sw_info.py` | `asset_sw_products` | 설치 소프트웨어 목록 |
| | `asset_sw_hotfixes` | 핫픽스/패치 목록 |
| | `asset_sw_processes` | 실행 프로세스 스냅샷 |
| `custom_field.py` | `asset_custom_fields` | 자산별 사용자 정의 필드 (key:value) |
| `layout.py` | `column_layouts` | 자산 목록 컬럼 레이아웃 저장 |
| `collect_script.py` | `collect_scripts` | PowerShell 수집 스크립트 메타데이터 |
| `report.py` | `report_templates` | 보고서 서식 (동적 컬럼 구성) |

### 자동 시드 데이터

| 테이블 | 시드 내용 | 조건 |
|--------|-----------|------|
| `collect_scripts` | 9개 (system/cpu/memory/disk/gpu/nic/product/hotfix/process) | 테이블 비어있을 때 |
| `report_templates` | 8개 기본 서식 (형상관리대장~비밀번호관리대장) | 테이블 비어있을 때 |

---

## 3. 자산코드 채번 규칙

```
형식: {ASSET_PREFIX}-{group_code}-{type_code}-{seq:04d}
예시: IC-GT1-SER-0001

규칙:
- group_nodes.code 가 설정된 노드만 자산 등록 가능
- asset_code_sequences 에서 SELECT FOR UPDATE → 원자적 증가
- 삭제된 자산의 번호 재사용 불가 (논리삭제)
```

---

## 4. API 엔드포인트 전체 목록

### 시스템
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/health` | 헬스체크 |

### 위치 트리
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/locations` | 전체 목록 |
| POST | `/api/locations` | 생성 |
| PATCH | `/api/locations/{id}` | 수정 |
| DELETE | `/api/locations/{id}` | 삭제 |

### 그룹 트리
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/groups` | 전체 목록 |
| POST | `/api/groups` | 생성 |
| PATCH | `/api/groups/{id}` | 수정 |
| DELETE | `/api/groups/{id}` | 삭제 |

### 자산
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/assets` | 목록 (group_id, status 필터) |
| GET | `/api/assets/enriched` | 목록 + 전체 조인 데이터 (32개 필드) |
| GET | `/api/assets/preview-code` | 자산코드 미리보기 (채번 없음) |
| GET | `/api/assets/bulk-template` | 대량 등록 엑셀 템플릿 다운로드 |
| POST | `/api/assets/bulk-register` | 대량 등록 (엑셀 업로드) |
| POST | `/api/assets` | 단건 등록 |
| GET | `/api/assets/{id}` | 단건 조회 |
| PATCH | `/api/assets/{id}` | 수정 (변경이력 자동 기록) |
| DELETE | `/api/assets/{id}` | 논리삭제 |
| GET | `/api/assets/{id}/change-log` | 변경 이력 조회 |

### HW 수집 정보
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/assets/{id}/hw/system` | 시스템 정보 |
| GET | `/api/assets/{id}/hw/cpus` | CPU 목록 |
| GET | `/api/assets/{id}/hw/memories` | 메모리 목록 |
| GET | `/api/assets/{id}/hw/disks` | 디스크 목록 |
| GET | `/api/assets/{id}/hw/gpus` | GPU 목록 |
| GET | `/api/assets/{id}/hw/nics` | NIC 목록 |

### SW 수집 정보
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/assets/{id}/sw/products` | 설치 프로그램 목록 |
| GET | `/api/assets/{id}/sw/hotfixes` | 핫픽스 목록 |
| GET | `/api/assets/{id}/sw/processes` | 프로세스 목록 |

### 사용자 정의 필드
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/assets/{id}/custom-fields` | 목록 |
| POST | `/api/assets/{id}/custom-fields` | 추가 |
| PATCH | `/api/assets/{id}/custom-fields/{field_id}` | 수정 |
| DELETE | `/api/assets/{id}/custom-fields/{field_id}` | 삭제 |

### 컬럼 레이아웃
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/layouts` | 저장된 레이아웃 목록 |
| POST | `/api/layouts` | 저장 |
| DELETE | `/api/layouts/{id}` | 삭제 |

### 카탈로그 (장비종류/OS/백신)
| Method | Path | 설명 |
|--------|------|------|
| GET/POST | `/api/catalogs/equipment-types` | 장비종류 |
| PATCH/DELETE | `/api/catalogs/equipment-types/{id}` | 장비종류 수정/삭제 |
| GET/POST | `/api/catalogs/os` | OS 카탈로그 |
| PATCH/DELETE | `/api/catalogs/os/{id}` | OS 수정/삭제 |
| GET/POST | `/api/catalogs/av` | 백신 카탈로그 |
| PATCH/DELETE | `/api/catalogs/av/{id}` | 백신 수정/삭제 |

### 담당자/부서
| Method | Path | 설명 |
|--------|------|------|
| GET/POST | `/api/persons/departments` | 부서 |
| PATCH/DELETE | `/api/persons/departments/{id}` | 부서 수정/삭제 |
| GET/POST | `/api/persons` | 담당자 |
| PATCH/DELETE | `/api/persons/{id}` | 담당자 수정/삭제 |

### 수집 스크립트
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/collect/scripts` | 스크립트 목록 (9개) |
| GET | `/api/collect/scripts/{key}/download` | 개별 스크립트 다운로드 (.ps1) |
| GET | `/api/collect/script-bundle` | 통합 스크립트 다운로드 |
| PATCH | `/api/collect/scripts/{key}` | 스크립트 수정 |
| POST | `/api/collect/upload` | 파일 업로드 (저장 없이) |
| POST | `/api/collect/parse-preview` | 파싱 미리보기 |
| POST | `/api/collect/confirm` | 파싱 후 DB 저장 |

### 보고서
| Method | Path | 설명 |
|--------|------|------|
| GET | `/api/reports/data-sources` | 사용 가능한 데이터소스 목록 |
| GET | `/api/reports/fields/{data_source}` | 해당 소스의 전체 필드 카탈로그 |
| GET/POST | `/api/reports/templates` | 서식 목록 / 생성 |
| GET/PATCH/DELETE | `/api/reports/templates/{id}` | 서식 조회/수정/삭제 |
| POST | `/api/reports/generate?template_id&year&month` | 보고서 생성 (xlsx 다운로드) |

### evtx 파서
| Method | Path | 설명 |
|--------|------|------|
| POST | `/api/evtx/upload` | .evtx 파일 업로드 → event_log_records 저장 |

---

## 5. 프론트엔드 페이지 & 컴포넌트

### 페이지 목록

| 경로 | 컴포넌트 | 설명 |
|------|----------|------|
| `/` | `DashboardPage.vue` | 대시보드 |
| `/assets` | `AssetListPage.vue` | 자산 현황 (전체 컬럼, 헤더 드래그) |
| `/assets/register` | `AssetRegisterPage.vue` | 자산 등록 (단건/대량) |
| `/assets/details?id=` | `AssetDetailPage.vue` | 자산 세부사항 (6탭) |
| `/reports` | `ReportPage.vue` | 보고서 생성 + 서식 관리 |
| `/reports/evtx` | `EvtxUploadPage.vue` | evtx 로그 업로드 |
| `/settings/locations` | `LocationTreePage.vue` | 위치 트리 관리 |
| `/settings/groups` | `GroupTreePage.vue` | 그룹 트리 관리 |
| `/settings/equipment-types` | `EquipmentTypePage.vue` | 장비종류 관리 |
| `/settings/os` | `OsCatalogPage.vue` | OS 카탈로그 관리 |
| `/settings/av` | `AvCatalogPage.vue` | 백신 카탈로그 관리 |
| `/settings/departments` | `DepartmentPage.vue` | 부서 관리 |
| `/settings/persons` | `PersonPage.vue` | 담당자 관리 |

### 자산 세부사항 탭 (AssetDetailPage)

| 탭 | 컴포넌트 | 기능 |
|----|----------|------|
| 기본정보 | `AssetBasicInfoTab.vue` | 자산 정보 편집, 저장, 삭제 |
| HW 정보 | `AssetHardwareTab.vue` | 수집된 HW 데이터 조회 |
| SW 정보 | `AssetSoftwareTab.vue` | 수집된 SW 데이터 조회 |
| 사용자 정의 | `AssetCustomFieldsTab.vue` | key:value 커스텀 필드 CRUD |
| 수집 업로드 | `AssetCollectUploadTab.vue` | PS1 스크립트 다운로드 + JSON/ZIP 업로드 |
| 변경 이력 | `AssetChangeLogTab.vue` | 자산 변경 이력 목록 |

### API 클라이언트 모듈

| 파일 | 담당 |
|------|------|
| `client.js` | Axios 인스턴스 (baseURL, 에러 인터셉터) |
| `assetsApi.js` | 자산 CRUD |
| `locationsApi.js` | 위치 트리 |
| `groupsApi.js` | 그룹 트리 |
| `catalogsApi.js` | 장비종류/OS/백신 |
| `personsApi.js` | 담당자 + 부서 |
| `layoutsApi.js` | 컬럼 레이아웃 |
| `hardwareApi.js` | HW 수집 데이터 |
| `softwareApi.js` | SW 수집 데이터 |
| `customFieldsApi.js` | 사용자 정의 필드 |
| `collectApi.js` | 수집 스크립트 + 업로드 |
| `reportsApi.js` | 보고서 서식 CRUD + 생성 |

### Pinia 스토어

| 파일 | 담당 |
|------|------|
| `locationStore.js` | 위치 트리 |
| `groupStore.js` | 그룹 트리 |
| `assetStore.js` | 자산 목록 |
| `catalogStore.js` | 장비종류/OS/백신 |
| `personStore.js` | 담당자/부서 (list, fetchList alias 포함) |
| `layoutStore.js` | 컬럼 레이아웃 |
| `assetHwStore.js` | HW 수집 데이터 |
| `assetSwStore.js` | SW 수집 데이터 |

---

## 6. 보고서 시스템 구조

### 동작 방식

```
보고서 생성 요청
  POST /api/reports/generate?template_id=1&year=2026&month=3
  ↓
report_templates 테이블에서 서식 로드
  ↓
data_source 별 fetcher 호출 (연도/월 필터)
  → list[dict] 반환 (32개 필드 포함)
  ↓
template.columns 순서대로 엑셀 렌더
  ↓
xlsx 파일 다운로드
```

### 데이터소스 8종

| 데이터소스 | 시기 필터 적용 | 다중시트 |
|-----------|--------------|---------|
| 형상관리대장 | ❌ (전체 현재 자산) | ❌ |
| 설비관리대장 | ❌ (전체 현재 자산) | ❌ |
| 예방점검_월간 | ✅ (record_date) | ✅ 월별 |
| 예방점검_분기 | ✅ (record_date) | ✅ 분기별 |
| 이벤트로그 | ✅ (record_date) | ✅ 월별 |
| 콘솔접속대장 | ✅ (access_date) | ❌ |
| 봉인지관리대장 | ✅ (record_date) | ❌ |
| 비밀번호관리대장 | ✅ (changed_date) | ❌ |

### 필드 카탈로그

- **형상관리대장/설비관리대장**: 32개 필드
  - assets: asset_code, asset_name, model_name, serial_number, ip_address, purpose, importance, status, install_date, created_at, updated_at, last_collected_at
  - group_nodes: group_name, group_full_path, group_code
  - location_nodes: location_name, location_full_path
  - equipment_types: equipment_type_name, equipment_type_code
  - os_catalog: os_name, os_version, os_eol_date, os_extended_eol
  - antivirus_catalog: av_name, av_version, av_support_end
  - persons(manager): manager_name, manager_title, manager_dept, manager_contact
  - persons(supervisor): supervisor_name, supervisor_title, supervisor_dept

---

## 7. 수집 스크립트 시스템

### PowerShell 수집 흐름

```
웹에서 스크립트 다운로드 (.ps1)
  ↓
대상 장비에서 실행 → JSON 파일 생성
  ↓
웹에서 JSON 업로드 (parse-preview → confirm)
  ↓
asset_hw_* / asset_sw_* 테이블에 저장
  assets.last_collected_at 갱신
```

### 9개 수집 스크립트

| key | 대상 테이블 | 수집 내용 |
|-----|-----------|---------|
| system | asset_hw_systems | 제조사/모델/S/N/OS/BIOS |
| cpu | asset_hw_cpus | CPU 모델/코어/클럭 |
| memory | asset_hw_memories | DIMM 슬롯별 용량/속도 |
| disk | asset_hw_disks | 디스크 모델/용량/인터페이스 |
| gpu | asset_hw_gpus | GPU 모델/드라이버/VRAM |
| nic | asset_hw_nics | NIC 이름/MAC/IP |
| product | asset_sw_products | 설치 프로그램 목록 |
| hotfix | asset_sw_hotfixes | KB 패치 목록 |
| process | asset_sw_processes | 실행 프로세스 스냅샷 |

---

## 8. 이번 세션에서 수정/추가된 사항

### 버그 픽스

| 커밋 | 문제 | 수정 내용 |
|------|------|----------|
| `73ee68e` | `/api/departments` 404 | `personsApi.js` 경로를 `/api/persons/departments`로 수정 |
| `73ee68e` | `personStore.fetchList is not a function` | `personStore.js`에 `list`, `fetchList` alias 추가 |
| `73ee68e` | DELETE 엔드포인트 누락 | `persons.py`, `catalogs.py`에 DELETE 라우트 전부 추가 |
| `73ee68e` | `DepartmentUpdate` 스키마 누락 | `schemas/master.py`에 추가 |
| `f852ce9` | `/api/collect/confirm` 500 오류 | collected_at ISO 문자열 → datetime 변환 (`_parse_datetime()` 추가) |
| `07bd260` | CORS 오류 (직접 IP 접근) | `docker-compose.yml`의 `VITE_API_URL` 빌드 arg 제거 → Nginx 상대경로 사용 |
| `2f85e2b` | `useDialog()` No outer provider | `App.vue`에 `<n-dialog-provider>` 추가 |
| `584246c` | evtx 업로드 413 오류 | `nginx.conf` `client_max_body_size 500M` 설정 |

### 신규 기능

| 커밋 | 기능 | 내용 |
|------|------|------|
| `e756b6b` | V2 전체 구현 | HW/SW 수집, 자산 세부사항 6탭, 수집 스크립트 시스템 |
| `a9aa605` | 장비종류 관리 페이지 | `EquipmentTypePage.vue` + API 경로 수정 |
| `66f1cbb` | 보고서 서식 관리 | `report_templates` 테이블, 동적 렌더러, 서식 CRUD UI |
| `8a83def` | 자산 목록 전체 컬럼 | `/api/assets/enriched` 32개 필드, 전체 컬럼 검색 |
| `be94426` | 컬럼 헤더 드래그 | 테이블 헤더 드래그앤드롭으로 컬럼 순서 변경 |

### 기존과 달라진 동작

| 항목 | 이전 | 현재 |
|------|------|------|
| **보고서 생성 파라미터** | `report_type` + `date_from` + `date_to` | `template_id` + `year` + `month(선택)` |
| **보고서 시기 필터** | 날짜 범위 | 연도 + 월(선택). 형상/설비관리대장은 시기 무관 전체 출력 |
| **자산 목록 데이터** | assets 테이블 raw 컬럼만 | `/enriched` API로 모든 조인 필드 포함 32개 |
| **컬럼 순서 변경** | 설정 팝오버 내 드래그 | 테이블 헤더 직접 드래그 |
| **검색 범위** | asset_code/asset_name만 | 표시 중인 전체 컬럼 or 특정 컬럼 선택 |
| **Nginx 업로드 제한** | 1MB (기본값) | 500MB |
| **API baseURL** | `VITE_API_URL=http://192.168.45.202:8000` | `''` (상대경로) → Nginx 프록시 경유 |

---

## 9. 파일 구조 (주요)

```
managing-facility-assets/
├── docker-compose.yml          # VITE_API_URL 빌드 arg 제거됨
├── .env                        # HOST_IP, POSTGRES_*, BACKEND_PORT
├── backend/
│   ├── app/
│   │   ├── main.py             # lifespan: DB생성 + 2개 시드 함수
│   │   ├── models/
│   │   │   ├── master.py       # 7개 마스터 테이블
│   │   │   ├── asset.py        # assets + 채번 + 변경이력
│   │   │   ├── record.py       # 5개 이력 테이블
│   │   │   ├── hw_info.py      # 6개 HW 테이블 [v2]
│   │   │   ├── sw_info.py      # 3개 SW 테이블 [v2]
│   │   │   ├── custom_field.py # 사용자 정의 필드 [v2]
│   │   │   ├── layout.py       # 컬럼 레이아웃 [v2]
│   │   │   ├── collect_script.py # 수집 스크립트 [v2]
│   │   │   └── report.py       # 보고서 서식 [신규]
│   │   ├── schemas/
│   │   │   ├── master.py       # DepartmentUpdate 추가됨
│   │   │   ├── asset.py
│   │   │   └── report.py       # ReportTemplate 스키마 [신규]
│   │   ├── api/routes/
│   │   │   ├── assets.py       # /enriched, /preview-code, /bulk-* 포함
│   │   │   ├── persons.py      # PATCH/DELETE 부서/담당자 추가됨
│   │   │   ├── catalogs.py     # DELETE 장비종류/OS/백신 추가됨
│   │   │   ├── reports.py      # 서식 CRUD + 동적 generate [전면개편]
│   │   │   ├── layouts.py      # [v2 신규]
│   │   │   ├── hardware.py     # [v2 신규]
│   │   │   ├── software.py     # [v2 신규]
│   │   │   ├── custom_fields.py # [v2 신규]
│   │   │   └── collect.py      # [v2 신규]
│   │   └── services/
│   │       ├── report_builder/
│   │       │   ├── __init__.py     # 동적 렌더러 [전면개편]
│   │       │   ├── field_catalog.py # 필드 카탈로그 [신규]
│   │       │   ├── data_fetchers.py # 데이터 fetcher [신규]
│   │       │   └── (기존 8개 빌더 파일은 참조용으로 유지)
│   │       ├── collect_parser.py   # _parse_datetime 추가됨
│   │       ├── script_generator.py # [v2 신규]
│   │       ├── asset_code.py
│   │       ├── bulk_register.py
│   │       └── change_logger.py
└── frontend/
    ├── nginx.conf              # client_max_body_size 500M 추가됨
    ├── Dockerfile              # ARG VITE_API_URL (빌드 시 빈 값)
    └── src/
        ├── App.vue             # n-dialog-provider 추가됨
        ├── api/                # 12개 API 모듈
        ├── stores/             # 8개 Pinia 스토어
        ├── pages/
        │   ├── assets/
        │   │   ├── AssetListPage.vue    # enriched + 헤더드래그 [전면개편]
        │   │   ├── AssetRegisterPage.vue # [v2 신규]
        │   │   ├── AssetDetailPage.vue  # [v2 신규]
        │   │   └── tabs/ (6개)
        │   ├── reports/
        │   │   └── ReportPage.vue       # 서식관리 탭 추가 [전면개편]
        │   └── settings/ (7개 페이지)
        └── components/
            ├── assets/
            │   ├── ColumnConfigPopover.vue # 체크박스만 (드래그 제거)
            │   ├── LayoutSelector.vue
            │   └── AssetCodePreview.vue
            └── layout/
                └── AppSidebar.vue
```

---

## 10. 알려진 제한사항 / 향후 고려사항

| 항목 | 현황 | 비고 |
|------|------|------|
| DB 마이그레이션 | `create_all` 방식 (Alembic 미사용) | 기존 컬럼 추가 시 수동 ALTER TABLE 필요 |
| 사용자 인증 | 미구현 | 폐쇄망 환경 가정 |
| 변경이력 changed_by | 하드코딩 `"system"` | 인증 구현 시 실제 사용자로 교체 필요 |
| 보고서 기존 빌더 파일 | `report_builder/*.py` 8개 유지 | 동적 렌더러로 교체됨, 삭제 가능 |
| SQLite | 사용 금지 | SELECT FOR UPDATE 미지원 |
| Streamlit | 사용 금지 | 멀티유저 CRUD 불가 |
