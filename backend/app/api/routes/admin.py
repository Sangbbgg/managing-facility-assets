"""
DB 관리 API — 테이블 목록·컬럼 정보·데이터 조회
개발/운영 편의 용도. 외부 노출 주의.
"""
from fastapi import APIRouter, HTTPException
from sqlalchemy import inspect as sa_inspect, text
from app.core.database import engine

router = APIRouter()


@router.get("/tables")
async def list_tables():
    """모든 테이블의 이름·컬럼·행 수를 반환합니다."""
    async with engine.connect() as conn:

        def _get_meta(sync_conn):
            inspector = sa_inspect(sync_conn)
            result = []
            for name in sorted(inspector.get_table_names()):
                cols = [
                    {"name": c["name"], "type": str(c["type"]), "nullable": c["nullable"]}
                    for c in inspector.get_columns(name)
                ]
                result.append({"name": name, "columns": cols, "rows": 0})
            return result

        tables = await conn.run_sync(_get_meta)

        for t in tables:
            row = await conn.execute(text(f'SELECT COUNT(*) FROM "{t["name"]}"'))
            t["rows"] = row.scalar()

    return tables


@router.get("/tables/{table_name}")
async def get_table_data(table_name: str, page: int = 1, size: int = 50):
    """테이블 데이터를 페이지네이션으로 반환합니다."""
    async with engine.connect() as conn:

        def _get_cols(sync_conn):
            inspector = sa_inspect(sync_conn)
            if table_name not in inspector.get_table_names():
                return None
            return [c["name"] for c in inspector.get_columns(table_name)]

        cols = await conn.run_sync(_get_cols)
        if cols is None:
            raise HTTPException(404, f"테이블 '{table_name}'을 찾을 수 없습니다")

        total = (await conn.execute(text(f'SELECT COUNT(*) FROM "{table_name}"'))).scalar()

        offset = (page - 1) * size
        order_col = "id" if "id" in cols else cols[0]
        rows_result = await conn.execute(
            text(f'SELECT * FROM "{table_name}" ORDER BY "{order_col}" LIMIT :size OFFSET :off'),
            {"size": size, "off": offset},
        )
        rows = [
            {k: (str(v) if v is not None and not isinstance(v, (int, float, bool, str)) else v)
             for k, v in row._mapping.items()}
            for row in rows_result
        ]

    return {"columns": cols, "rows": rows, "total": total, "page": page, "size": size}
