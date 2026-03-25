"""
자동 스키마 싱크 — 앱 시작 시 모델에 추가된 컬럼을 DB에 반영합니다.
- 새 테이블: create_all 이 처리
- 새 컬럼:   ALTER TABLE ... ADD COLUMN (NULL 허용으로 추가)
- 컬럼 삭제/수정: 지원하지 않음 (수동 마이그레이션 필요)
"""
import logging
from sqlalchemy import inspect as sa_inspect, text
from sqlalchemy.ext.asyncio import AsyncEngine
from app.models import Base

logger = logging.getLogger(__name__)


def _col_ddl(col) -> str:
    """SQLAlchemy 컬럼 → PostgreSQL 타입 문자열"""
    from sqlalchemy import String, Integer, BigInteger, Boolean, Date, DateTime, Text, JSON, Float, Numeric
    t = col.type
    if isinstance(t, String):    return f"VARCHAR({t.length or 255})"
    if isinstance(t, BigInteger):return "BIGINT"
    if isinstance(t, Integer):   return "INTEGER"
    if isinstance(t, Boolean):   return "BOOLEAN"
    if isinstance(t, Date):      return "DATE"
    if isinstance(t, DateTime):  return "TIMESTAMP"
    if isinstance(t, Text):      return "TEXT"
    if isinstance(t, (JSON,)):   return "JSONB"
    if isinstance(t, Float):     return "FLOAT"
    if isinstance(t, Numeric):   return f"NUMERIC({t.precision or 10},{t.scale or 2})"
    return "TEXT"  # 알 수 없는 타입은 TEXT로 대체


async def sync_schema(engine: AsyncEngine) -> None:
    """모델과 DB 컬럼을 비교해 누락된 컬럼을 ADD COLUMN으로 추가합니다."""
    async with engine.begin() as conn:

        def _detect(sync_conn):
            inspector = sa_inspect(sync_conn)
            existing_tables = set(inspector.get_table_names())
            stmts = []
            for table in Base.metadata.sorted_tables:
                if table.name not in existing_tables:
                    continue  # 새 테이블은 create_all 담당
                existing_cols = {c["name"] for c in inspector.get_columns(table.name)}
                for col in table.columns:
                    if col.name not in existing_cols:
                        ddl = _col_ddl(col)
                        stmts.append(
                            f'ALTER TABLE "{table.name}" ADD COLUMN "{col.name}" {ddl} NULL'
                        )
            return stmts

        stmts = await conn.run_sync(_detect)

        for stmt in stmts:
            logger.info(f"[schema_sync] {stmt}")
            await conn.execute(text(stmt))

        if stmts:
            logger.info(f"[schema_sync] {len(stmts)}개 컬럼 추가 완료")
        else:
            logger.info("[schema_sync] 스키마 최신 상태 — 변경 없음")
