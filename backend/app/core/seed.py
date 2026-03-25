"""
초기 seed 데이터 — DB가 비어있을 때만 삽입됩니다.
각 테이블에 데이터가 1건 이상 있으면 해당 테이블은 건너뜁니다.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# ── location_nodes ─────────────────────────────────────────────────────────
# id  name              parent_id  full_path                                                          depth
_LOCATION_NODES = [
    # depth 0
    ( 1, "신인천빛드림본부", None, "신인천빛드림본부",                                                   0),
    # depth 1
    ( 2, "발전제어",          1,   "신인천빛드림본부 > 발전제어",                                         1),
    ( 3, "연료전지",          1,   "신인천빛드림본부 > 연료전지",                                         1),
    # depth 2 — 발전제어 하위
    ( 4, "1단계",             2,   "신인천빛드림본부 > 발전제어 > 1단계",                                 2),
    ( 5, "2단계",             2,   "신인천빛드림본부 > 발전제어 > 2단계",                                 2),
    # depth 2 — 연료전지 하위
    ( 6, "1단계",             3,   "신인천빛드림본부 > 연료전지 > 1단계",                                 2),
    ( 7, "2단계",             3,   "신인천빛드림본부 > 연료전지 > 2단계",                                 2),
    ( 8, "3단계",             3,   "신인천빛드림본부 > 연료전지 > 3단계",                                 2),
    ( 9, "4단계",             3,   "신인천빛드림본부 > 연료전지 > 4단계",                                 2),
    (10, "5단계",             3,   "신인천빛드림본부 > 연료전지 > 5단계",                                 2),
    (11, "통합제어실",        3,   "신인천빛드림본부 > 연료전지 > 통합제어실",                            2),
    # depth 3 — 발전제어 > 1단계 하위
    (12, "전자기기실",        4,   "신인천빛드림본부 > 발전제어 > 1단계 > 전자기기실",                    3),
    (13, "전산실",            4,   "신인천빛드림본부 > 발전제어 > 1단계 > 전산실",                        3),
    (14, "중앙제어실",        4,   "신인천빛드림본부 > 발전제어 > 1단계 > 중앙제어실",                    3),
    (15, "발전운전원실",      4,   "신인천빛드림본부 > 발전제어 > 1단계 > 발전운전원실",                  3),
    (16, "GT1 Room",          4,   "신인천빛드림본부 > 발전제어 > 1단계 > GT1 Room",                      3),
    (17, "GT2 Room",          4,   "신인천빛드림본부 > 발전제어 > 1단계 > GT2 Room",                      3),
    (18, "GT3 Room",          4,   "신인천빛드림본부 > 발전제어 > 1단계 > GT3 Room",                      3),
    (19, "GT4 Room",          4,   "신인천빛드림본부 > 발전제어 > 1단계 > GT4 Room",                      3),
    (20, "GT1 EX Room",       4,   "신인천빛드림본부 > 발전제어 > 1단계 > GT1 EX Room",                  3),
    (21, "GT2 EX Room",       4,   "신인천빛드림본부 > 발전제어 > 1단계 > GT2 EX Room",                  3),
    (22, "GT3 EX Room",       4,   "신인천빛드림본부 > 발전제어 > 1단계 > GT3 EX Room",                  3),
    (23, "GT4 EX Room",       4,   "신인천빛드림본부 > 발전제어 > 1단계 > GT4 EX Room",                  3),
    (24, "ST1 EX Room",       4,   "신인천빛드림본부 > 발전제어 > 1단계 > ST1 EX Room",                  3),
    # depth 3 — 발전제어 > 2단계 하위
    (25, "전자기기실",        5,   "신인천빛드림본부 > 발전제어 > 2단계 > 전자기기실",                    3),
    (26, "전산실",            5,   "신인천빛드림본부 > 발전제어 > 2단계 > 전산실",                        3),
    (27, "중앙제어실",        5,   "신인천빛드림본부 > 발전제어 > 2단계 > 중앙제어실",                    3),
    (28, "발전운전원실",      5,   "신인천빛드림본부 > 발전제어 > 2단계 > 발전운전원실",                  3),
    (29, "GT5 Room",          5,   "신인천빛드림본부 > 발전제어 > 2단계 > GT5 Room",                      3),
    (30, "GT6 Room",          5,   "신인천빛드림본부 > 발전제어 > 2단계 > GT6 Room",                      3),
    (31, "GT7 Room",          5,   "신인천빛드림본부 > 발전제어 > 2단계 > GT7 Room",                      3),
    (32, "GT8 Room",          5,   "신인천빛드림본부 > 발전제어 > 2단계 > GT8 Room",                      3),
    (33, "GT5 EX Room",       5,   "신인천빛드림본부 > 발전제어 > 2단계 > GT5 EX Room",                  3),
    (34, "GT6 EX Room",       5,   "신인천빛드림본부 > 발전제어 > 2단계 > GT6 EX Room",                  3),
    (35, "GT7 EX Room",       5,   "신인천빛드림본부 > 발전제어 > 2단계 > GT7 EX Room",                  3),
    (36, "GT8 EX Room",       5,   "신인천빛드림본부 > 발전제어 > 2단계 > GT8 EX Room",                  3),
]


# ── group_nodes ────────────────────────────────────────────────────────────
# id  name              code    parent_id  full_path                                                                depth
_GROUP_NODES = [
    # depth 0
    ( 1, "신인천빛드림본부", None, None, "신인천빛드림본부",                                                        0),
    # depth 1
    ( 2, "발전제어",        None,    1,  "신인천빛드림본부 > 발전제어",                                              1),
    ( 3, "연료전지",        "SA",    1,  "신인천빛드림본부 > 연료전지",                                              1),
    # depth 2 — 발전제어 하위
    ( 4, "1단계",           None,    2,  "신인천빛드림본부 > 발전제어 > 1단계",                                      2),
    ( 5, "2단계",           None,    2,  "신인천빛드림본부 > 발전제어 > 2단계",                                      2),
    (16, "기타",            "COM",   2,  "신인천빛드림본부 > 발전제어 > 기타",                                       2),
    # depth 3 — 발전제어 > 1단계 하위
    ( 6, "1CC",             None,    4,  "신인천빛드림본부 > 발전제어 > 1단계 > 1CC",                                3),
    ( 7, "2CC",             None,    4,  "신인천빛드림본부 > 발전제어 > 1단계 > 2CC",                                3),
    ( 8, "1단계 DCS",       "BR1",   4,  "신인천빛드림본부 > 발전제어 > 1단계 > 1단계 DCS",                         3),
    # depth 3 — 발전제어 > 2단계 하위
    ( 9, "3CC",             None,    5,  "신인천빛드림본부 > 발전제어 > 2단계 > 3CC",                                3),
    (10, "4CC",             None,    5,  "신인천빛드림본부 > 발전제어 > 2단계 > 4CC",                                3),
    (11, "2단계 DCS",       "BR2",   5,  "신인천빛드림본부 > 발전제어 > 2단계 > 2단계 DCS",                         3),
    # depth 4 — 1CC 하위
    (12, "1ST",             "ST1",   6,  "신인천빛드림본부 > 발전제어 > 1단계 > 1CC > 1ST",                         4),
    (13, "GT",              "GT1",   6,  "신인천빛드림본부 > 발전제어 > 1단계 > 1CC > 1~2GT",                           4),
    # depth 4 — 2CC 하위
    (14, "2ST",             "ST2",   7,  "신인천빛드림본부 > 발전제어 > 1단계 > 2CC > 2ST",                         4),
    (15, "GT",              "GT2",   7,  "신인천빛드림본부 > 발전제어 > 1단계 > 2CC > 3~4GT",                           4),
    # depth 4 — 3CC 하위
    (17, "3ST",             "ST3",   9,  "신인천빛드림본부 > 발전제어 > 2단계 > 3CC > 3ST",                          4),
    (18, "5~6GT",           "GT3",   9,  "신인천빛드림본부 > 발전제어 > 2단계 > 3CC > 5~6GT",                        4),
    # depth 4 — 4CC 하위
    (19, "4ST",             "ST4",  10,  "신인천빛드림본부 > 발전제어 > 2단계 > 4CC > 4ST",                          4),
    (20, "7~8GT",           "GT4",  10,  "신인천빛드림본부 > 발전제어 > 2단계 > 4CC > 7~8GT",                        4),
    # depth 4 — 1CC 하위
    (21, "1EG",             "EG1",   6,  "신인천빛드림본부 > 발전제어 > 1단계 > 1CC > 1EG",                          4),
    # depth 4 — 2CC 하위
    (22, "2EG",             "EG2",   7,  "신인천빛드림본부 > 발전제어 > 1단계 > 2CC > 2EG",                          4),
    # depth 4 — 3CC 하위
    (23, "3EG",             "EG3",   9,  "신인천빛드림본부 > 발전제어 > 2단계 > 3CC > 3EG",                          4),
    # depth 4 — 4CC 하위
    (24, "4EG",             "EG4",  10,  "신인천빛드림본부 > 발전제어 > 2단계 > 4CC > 4EG",                          4),
]


async def seed_location_nodes(session: AsyncSession) -> None:
    result = await session.execute(text("SELECT COUNT(*) FROM location_nodes"))
    if result.scalar() > 0:
        return

    await session.execute(text("""
        INSERT INTO location_nodes (id, name, parent_id, full_path, depth)
        VALUES (:id, :name, :parent_id, :full_path, :depth)
    """), [
        {"id": r[0], "name": r[1], "parent_id": r[2], "full_path": r[3], "depth": r[4]}
        for r in _LOCATION_NODES
    ])
    await session.execute(text(
        "SELECT setval(pg_get_serial_sequence('location_nodes','id'), MAX(id)) FROM location_nodes"
    ))
    await session.commit()


async def seed_group_nodes(session: AsyncSession) -> None:
    result = await session.execute(text("SELECT COUNT(*) FROM group_nodes"))
    if result.scalar() > 0:
        return

    await session.execute(text("""
        INSERT INTO group_nodes (id, name, code, parent_id, full_path, depth)
        VALUES (:id, :name, :code, :parent_id, :full_path, :depth)
    """), [
        {"id": r[0], "name": r[1], "code": r[2], "parent_id": r[3], "full_path": r[4], "depth": r[5]}
        for r in _GROUP_NODES
    ])
    await session.execute(text(
        "SELECT setval(pg_get_serial_sequence('group_nodes','id'), MAX(id)) FROM group_nodes"
    ))
    await session.commit()


# ── equipment_types ─────────────────────────────────────────────────────────
# id  name              code
_EQUIPMENT_TYPES = [
    (1, "SERVER",         "SER"),
    (2, "PC",             "PC"),
    (3, "Network Switch", "NW"),
    (4, "기타",           "ETC"),
    (5, "보안",           "SEC"),
    (7, "Controller",     "CD"),
]


# ── departments ──────────────────────────────────────────────────────────────
# id  name            code
_DEPARTMENTS = [
    (1, "계측제어부",   None),
    (2, "신재생운영팀", None),
    (3, "전기부",       None),
]


async def seed_equipment_types(session: AsyncSession) -> None:
    result = await session.execute(text("SELECT COUNT(*) FROM equipment_types"))
    if result.scalar() > 0:
        return

    await session.execute(text("""
        INSERT INTO equipment_types (id, name, code)
        VALUES (:id, :name, :code)
    """), [
        {"id": r[0], "name": r[1], "code": r[2]}
        for r in _EQUIPMENT_TYPES
    ])
    await session.execute(text(
        "SELECT setval(pg_get_serial_sequence('equipment_types','id'), MAX(id)) FROM equipment_types"
    ))
    await session.commit()


async def seed_departments(session: AsyncSession) -> None:
    result = await session.execute(text("SELECT COUNT(*) FROM departments"))
    if result.scalar() > 0:
        return

    await session.execute(text("""
        INSERT INTO departments (id, name, code)
        VALUES (:id, :name, :code)
    """), [
        {"id": r[0], "name": r[1], "code": r[2]}
        for r in _DEPARTMENTS
    ])
    await session.execute(text(
        "SELECT setval(pg_get_serial_sequence('departments','id'), MAX(id)) FROM departments"
    ))
    await session.commit()
