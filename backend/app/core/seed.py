"""
Default seed helpers.

The current DB is reset before seed data is inserted so startup always returns
the seeded master-data state.
"""
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


_LOCATION_NODES = [
    {"id": 1, "parent_id": None, "name": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80", "depth": 0},
    {"id": 2, "parent_id": 1, "name": "\ubc1c\uc804\uc81c\uc5b4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4", "depth": 1},
    {"id": 3, "parent_id": 1, "name": "\uc5f0\ub8cc\uc804\uc9c0", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc5f0\ub8cc\uc804\uc9c0", "depth": 1},
    {"id": 4, "parent_id": 2, "name": "1\ub2e8\uacc4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4", "depth": 2},
    {"id": 5, "parent_id": 2, "name": "2\ub2e8\uacc4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4", "depth": 2},
    {"id": 6, "parent_id": 2, "name": "\ubcf8\uad00", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \ubcf8\uad00", "depth": 2},
    {"id": 7, "parent_id": 3, "name": "\uc5f0\ub8cc\uc804\uc9c0 1\ub2e8\uacc4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc5f0\ub8cc\uc804\uc9c0 > \uc5f0\ub8cc\uc804\uc9c0 1\ub2e8\uacc4", "depth": 2},
    {"id": 8, "parent_id": 3, "name": "\uc5f0\ub8cc\uc804\uc9c0 2\ub2e8\uacc4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc5f0\ub8cc\uc804\uc9c0 > \uc5f0\ub8cc\uc804\uc9c0 2\ub2e8\uacc4", "depth": 2},
    {"id": 9, "parent_id": 3, "name": "\uc5f0\ub8cc\uc804\uc9c0 3\ub2e8\uacc4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc5f0\ub8cc\uc804\uc9c0 > \uc5f0\ub8cc\uc804\uc9c0 3\ub2e8\uacc4", "depth": 2},
    {"id": 10, "parent_id": 3, "name": "\uc5f0\ub8cc\uc804\uc9c0 4\ub2e8\uacc4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc5f0\ub8cc\uc804\uc9c0 > \uc5f0\ub8cc\uc804\uc9c0 4\ub2e8\uacc4", "depth": 2},
    {"id": 11, "parent_id": 3, "name": "\uc5f0\ub8cc\uc804\uc9c0 5\ub2e8\uacc4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc5f0\ub8cc\uc804\uc9c0 > \uc5f0\ub8cc\uc804\uc9c0 5\ub2e8\uacc4", "depth": 2},
    {"id": 12, "parent_id": 3, "name": "\uc5f0\ub8cc\uc804\uc9c0 \ud1b5\ud569\uc81c\uc5b4\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc5f0\ub8cc\uc804\uc9c0 > \uc5f0\ub8cc\uc804\uc9c0 \ud1b5\ud569\uc81c\uc5b4\uc2e4", "depth": 2},
    {"id": 13, "parent_id": 4, "name": "1\ub2e8\uacc4 \uc804\uc790\uae30\uae30\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > 1\ub2e8\uacc4 \uc804\uc790\uae30\uae30\uc2e4", "depth": 3},
    {"id": 14, "parent_id": 4, "name": "1\ub2e8\uacc4 \uc804\uc0b0\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > 1\ub2e8\uacc4 \uc804\uc0b0\uc2e4", "depth": 3},
    {"id": 15, "parent_id": 4, "name": "1\ub2e8\uacc4 \uc911\uc559\uc81c\uc5b4\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > 1\ub2e8\uacc4 \uc911\uc559\uc81c\uc5b4\uc2e4", "depth": 3},
    {"id": 16, "parent_id": 4, "name": "1\ub2e8\uacc4 \ubc1c\uc804\uc6b4\uc804\uc6d0\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > 1\ub2e8\uacc4 \ubc1c\uc804\uc6b4\uc804\uc6d0\uc2e4", "depth": 3},
    {"id": 17, "parent_id": 4, "name": "GT1 Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > GT1 Room", "depth": 3},
    {"id": 18, "parent_id": 4, "name": "GT2 Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > GT2 Room", "depth": 3},
    {"id": 19, "parent_id": 4, "name": "GT3 Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > GT3 Room", "depth": 3},
    {"id": 20, "parent_id": 4, "name": "GT4 Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > GT4 Room", "depth": 3},
    {"id": 21, "parent_id": 4, "name": "GT1 EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > GT1 EX Room", "depth": 3},
    {"id": 22, "parent_id": 4, "name": "GT2 EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > GT2 EX Room", "depth": 3},
    {"id": 23, "parent_id": 4, "name": "GT3 EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > GT3 EX Room", "depth": 3},
    {"id": 24, "parent_id": 4, "name": "GT4 EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > GT4 EX Room", "depth": 3},
    {"id": 25, "parent_id": 4, "name": "1ST EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > 1ST EX Room", "depth": 3},
    {"id": 26, "parent_id": 4, "name": "2ST EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 1\ub2e8\uacc4 > 2ST EX Room", "depth": 3},
    {"id": 27, "parent_id": 5, "name": "2\ub2e8\uacc4 \uc804\uc790\uae30\uae30\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > 2\ub2e8\uacc4 \uc804\uc790\uae30\uae30\uc2e4", "depth": 3},
    {"id": 28, "parent_id": 5, "name": "2\ub2e8\uacc4 \uc804\uc0b0\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > 2\ub2e8\uacc4 \uc804\uc0b0\uc2e4", "depth": 3},
    {"id": 29, "parent_id": 5, "name": "2\ub2e8\uacc4 \uc911\uc559\uc81c\uc5b4\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > 2\ub2e8\uacc4 \uc911\uc559\uc81c\uc5b4\uc2e4", "depth": 3},
    {"id": 30, "parent_id": 5, "name": "2\ub2e8\uacc4 \ubc1c\uc804\uc6b4\uc804\uc6d0\uc2e4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > 2\ub2e8\uacc4 \ubc1c\uc804\uc6b4\uc804\uc6d0\uc2e4", "depth": 3},
    {"id": 31, "parent_id": 5, "name": "GT5 Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > GT5 Room", "depth": 3},
    {"id": 32, "parent_id": 5, "name": "GT6 Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > GT6 Room", "depth": 3},
    {"id": 33, "parent_id": 5, "name": "GT7 Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > GT7 Room", "depth": 3},
    {"id": 34, "parent_id": 5, "name": "GT8 Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > GT8 Room", "depth": 3},
    {"id": 35, "parent_id": 5, "name": "GT5 EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > GT5 EX Room", "depth": 3},
    {"id": 36, "parent_id": 5, "name": "GT6 EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > GT6 EX Room", "depth": 3},
    {"id": 37, "parent_id": 5, "name": "GT7 EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > GT7 EX Room", "depth": 3},
    {"id": 38, "parent_id": 5, "name": "GT8 EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > GT8 EX Room", "depth": 3},
    {"id": 39, "parent_id": 5, "name": "3ST EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > 3ST EX Room", "depth": 3},
    {"id": 40, "parent_id": 5, "name": "4ST EX Room", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > 2\ub2e8\uacc4 > 4ST EX Room", "depth": 3},
    {"id": 41, "parent_id": 6, "name": "3\uce35 \uacc4\uce21\uc81c\uc5b4\ubd80", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \ubcf8\uad00 > 3\uce35 \uacc4\uce21\uc81c\uc5b4\ubd80", "depth": 3},
    {"id": 42, "parent_id": 6, "name": "\ub0b4\ud654\uae08\uace0", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \ubcf8\uad00 > \ub0b4\ud654\uae08\uace0", "depth": 3},
]

_GROUP_NODES = [
    {"id": 1, "parent_id": None, "name": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80", "depth": 0, "display_code": None},
    {"id": 2, "parent_id": 1, "name": "\ubc1c\uc804\uc81c\uc5b4", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4", "depth": 1, "display_code": None},
    {"id": 3, "parent_id": 2, "name": "\uae30\ubc18", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18", "depth": 2, "display_code": None},
    {"id": 4, "parent_id": 3, "name": "1\ub2e8\uacc4", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4", "depth": 3, "display_code": None},
    {"id": 5, "parent_id": 4, "name": "1CC", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 1CC", "depth": 4, "display_code": None},
    {"id": 6, "parent_id": 5, "name": "1ST", "code": "ST1", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 1CC > 1ST", "depth": 5, "display_code": "ST1"},
    {"id": 7, "parent_id": 5, "name": "1~2GT", "code": "GT1", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 1CC > 1~2GT", "depth": 5, "display_code": "GT1"},
    {"id": 8, "parent_id": 5, "name": "1CC \uc5ec\uc790\uae30", "code": "EG1", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 1CC > 1CC \uc5ec\uc790\uae30", "depth": 5, "display_code": "EG1"},
    {"id": 9, "parent_id": 4, "name": "2CC", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 2CC", "depth": 4, "display_code": None},
    {"id": 10, "parent_id": 9, "name": "2ST", "code": "ST2", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 2CC > 2ST", "depth": 5, "display_code": "ST2"},
    {"id": 11, "parent_id": 9, "name": "3~4GT", "code": "GT2", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 2CC > 3~4GT", "depth": 5, "display_code": "GT2"},
    {"id": 12, "parent_id": 9, "name": "2CC \uc5ec\uc790\uae30", "code": "EG2", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 2CC > 2CC \uc5ec\uc790\uae30", "depth": 5, "display_code": "EG2"},
    {"id": 13, "parent_id": 4, "name": "1\ub2e8\uacc4 DCS", "code": "BR1", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 1\ub2e8\uacc4 DCS", "depth": 4, "display_code": "BR1"},
    {"id": 14, "parent_id": 4, "name": "1\ub2e8\uacc4 ECMS", "code": "ECMS1", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 1\ub2e8\uacc4 > 1\ub2e8\uacc4 ECMS", "depth": 4, "display_code": "ECMS1"},
    {"id": 15, "parent_id": 3, "name": "2\ub2e8\uacc4", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4", "depth": 3, "display_code": None},
    {"id": 16, "parent_id": 15, "name": "3CC", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 3CC", "depth": 4, "display_code": None},
    {"id": 17, "parent_id": 16, "name": "3ST", "code": "ST3", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 3CC > 3ST", "depth": 5, "display_code": "ST3"},
    {"id": 18, "parent_id": 16, "name": "5~6GT", "code": "GT3", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 3CC > 5~6GT", "depth": 5, "display_code": "GT3"},
    {"id": 19, "parent_id": 16, "name": "3CC \uc5ec\uc790\uae30", "code": "EG3", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 3CC > 3CC \uc5ec\uc790\uae30", "depth": 5, "display_code": "EG3"},
    {"id": 20, "parent_id": 15, "name": "4CC", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 4CC", "depth": 4, "display_code": None},
    {"id": 21, "parent_id": 20, "name": "4ST", "code": "ST4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 4CC > 4ST", "depth": 5, "display_code": "ST4"},
    {"id": 22, "parent_id": 20, "name": "7~8GT", "code": "GT4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 4CC > 7~8GT", "depth": 5, "display_code": "GT4"},
    {"id": 23, "parent_id": 20, "name": "4CC \uc5ec\uc790\uae30", "code": "EG4", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 4CC > 4CC \uc5ec\uc790\uae30", "depth": 5, "display_code": "EG4"},
    {"id": 24, "parent_id": 15, "name": "2\ub2e8\uacc4 DCS", "code": "BR2", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 2\ub2e8\uacc4 DCS", "depth": 4, "display_code": "BR2"},
    {"id": 25, "parent_id": 15, "name": "2\ub2e8\uacc4 ECMS", "code": "ECMS2", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > 2\ub2e8\uacc4 > 2\ub2e8\uacc4 ECMS", "depth": 4, "display_code": "ECMS2"},
    {"id": 26, "parent_id": 3, "name": "\uacf5\ud1b5", "code": "COM", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \uae30\ubc18 > \uacf5\ud1b5", "depth": 3, "display_code": "COM"},
    {"id": 27, "parent_id": 2, "name": "\ube44\uae30\ubc18", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \ubc1c\uc804\uc81c\uc5b4 > \ube44\uae30\ubc18", "depth": 2, "display_code": None},
    {"id": 28, "parent_id": 1, "name": "\uc2e0\uc7ac\uc0dd\uc5d0\ub108\uc9c0", "code": None, "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc2e0\uc7ac\uc0dd\uc5d0\ub108\uc9c0", "depth": 1, "display_code": None},
    {"id": 29, "parent_id": 28, "name": "\uc5f0\ub8cc\uc804\uc9c0", "code": "SA", "full_path": "\uc2e0\uc778\ucc9c\ube5b\ub4dc\ub9bc\ubcf8\ubd80 > \uc2e0\uc7ac\uc0dd\uc5d0\ub108\uc9c0 > \uc5f0\ub8cc\uc804\uc9c0", "depth": 2, "display_code": "SA"},
]

_EQUIPMENT_TYPES = [
    {"id": 1, "name": "SERVER", "code": "SER", "description": None},
    {"id": 2, "name": "PC", "code": "PC", "description": None},
    {"id": 3, "name": "Network Switch", "code": "NW", "description": None},
    {"id": 4, "name": "\uae30\ud0c0", "code": "ETC", "description": None},
    {"id": 5, "name": "\ubcf4\uc548", "code": "SEC", "description": None},
    {"id": 7, "name": "Controller", "code": "CD", "description": None},
]

_DEPARTMENTS = [
    {"id": 1, "name": "\uacc4\uce21\uc81c\uc5b4\ubd80", "code": None},
    {"id": 2, "name": "\uc2e0\uc7ac\uc0dd\uc6b4\uc601\ud300", "code": None},
    {"id": 3, "name": "\uc804\uae30\ubd80", "code": None},
]

_PERSONS = [
    {"id": 1, "dept_id": 1, "name": "\uae40\uac00\uc6d0", "title": "", "contact": ""},
    {"id": 2, "dept_id": 1, "name": "\ucd5c\ubd80\uc601", "title": "", "contact": ""},
    {"id": 3, "dept_id": 1, "name": "\uae40\uacbd\ub82c", "title": "", "contact": ""},
    {"id": 4, "dept_id": 1, "name": "\ubc15\uaddc\ud604", "title": "", "contact": ""},
    {"id": 5, "dept_id": 3, "name": "\ucd5c\uc81c\uc77c", "title": "", "contact": ""},
    {"id": 6, "dept_id": 3, "name": "\uc804\uc0c1\ub9cc", "title": "", "contact": ""},
    {"id": 7, "dept_id": 2, "name": "\uc774\uc131\ud638", "title": "", "contact": ""},
]

_PERSON_GROUP_ROLES = [
    {"id": 18, "person_id": 1, "group_id": 24, "role_type": "PRIMARY"},
    {"id": 19, "person_id": 1, "group_id": 17, "role_type": "PRIMARY"},
    {"id": 20, "person_id": 1, "group_id": 21, "role_type": "PRIMARY"},
    {"id": 21, "person_id": 1, "group_id": 26, "role_type": "PRIMARY"},
    {"id": 22, "person_id": 2, "group_id": 13, "role_type": "PRIMARY"},
    {"id": 23, "person_id": 2, "group_id": 6, "role_type": "PRIMARY"},
    {"id": 24, "person_id": 2, "group_id": 10, "role_type": "PRIMARY"},
    {"id": 25, "person_id": 2, "group_id": 26, "role_type": "PRIMARY"},
    {"id": 26, "person_id": 3, "group_id": 7, "role_type": "PRIMARY"},
    {"id": 27, "person_id": 3, "group_id": 11, "role_type": "PRIMARY"},
    {"id": 28, "person_id": 4, "group_id": 18, "role_type": "PRIMARY"},
    {"id": 29, "person_id": 4, "group_id": 22, "role_type": "PRIMARY"},
    {"id": 30, "person_id": 5, "group_id": 21, "role_type": "PRIMARY"},
    {"id": 31, "person_id": 5, "group_id": 12, "role_type": "PRIMARY"},
    {"id": 32, "person_id": 6, "group_id": 29, "role_type": "PRIMARY"},
    {"id": 33, "person_id": 7, "group_id": 19, "role_type": "PRIMARY"},
    {"id": 34, "person_id": 7, "group_id": 23, "role_type": "PRIMARY"},
]


_SEED_ROOT_TABLES = (
    "location_nodes",
    "group_nodes",
    "equipment_types",
    "departments",
    "persons",
    "person_group_roles",
)

_RESET_ONLY_TABLES = (
    "asset_code_sequences",
)


async def _table_has_rows(session: AsyncSession, table_name: str) -> bool:
    result = await session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
    return (result.scalar() or 0) > 0


async def _sync_sequence(session: AsyncSession, table_name: str) -> None:
    await session.execute(
        text(
            f"SELECT setval(pg_get_serial_sequence('{table_name}','id'), "
            f"COALESCE((SELECT MAX(id) FROM {table_name}), 1))"
        )
    )


async def reset_seeded_db(session: AsyncSession) -> None:
    reset_tables = _SEED_ROOT_TABLES + _RESET_ONLY_TABLES
    quoted_tables = ", ".join(f'"{table_name}"' for table_name in reset_tables)
    await session.execute(text(f"TRUNCATE TABLE {quoted_tables} RESTART IDENTITY CASCADE"))
    await session.commit()


async def is_seed_data_missing(session: AsyncSession) -> bool:
    for table_name in _SEED_ROOT_TABLES:
        if not await _table_has_rows(session, table_name):
            return True
    return False


async def seed_location_nodes(session: AsyncSession) -> None:
    if await _table_has_rows(session, "location_nodes"):
        return

    await session.execute(
        text(
            """
            INSERT INTO location_nodes (id, parent_id, name, full_path, depth)
            VALUES (:id, :parent_id, :name, :full_path, :depth)
            """
        ),
        _LOCATION_NODES,
    )
    await _sync_sequence(session, "location_nodes")
    await session.commit()


async def seed_group_nodes(session: AsyncSession) -> None:
    if await _table_has_rows(session, "group_nodes"):
        return

    await session.execute(
        text(
            """
            INSERT INTO group_nodes (id, parent_id, name, code, full_path, depth, display_code)
            VALUES (:id, :parent_id, :name, :code, :full_path, :depth, :display_code)
            """
        ),
        _GROUP_NODES,
    )
    await _sync_sequence(session, "group_nodes")
    await session.commit()


async def seed_equipment_types(session: AsyncSession) -> None:
    if await _table_has_rows(session, "equipment_types"):
        return

    await session.execute(
        text(
            """
            INSERT INTO equipment_types (id, name, code, description)
            VALUES (:id, :name, :code, :description)
            """
        ),
        _EQUIPMENT_TYPES,
    )
    await _sync_sequence(session, "equipment_types")
    await session.commit()


async def seed_departments(session: AsyncSession) -> None:
    if await _table_has_rows(session, "departments"):
        return

    await session.execute(
        text(
            """
            INSERT INTO departments (id, name, code)
            VALUES (:id, :name, :code)
            """
        ),
        _DEPARTMENTS,
    )
    await _sync_sequence(session, "departments")
    await session.commit()


async def seed_persons(session: AsyncSession) -> None:
    if await _table_has_rows(session, "persons"):
        return

    await session.execute(
        text(
            """
            INSERT INTO persons (id, dept_id, name, title, contact)
            VALUES (:id, :dept_id, :name, :title, :contact)
            """
        ),
        _PERSONS,
    )
    await _sync_sequence(session, "persons")
    await session.commit()


async def seed_person_group_roles(session: AsyncSession) -> None:
    if await _table_has_rows(session, "person_group_roles"):
        return

    await session.execute(
        text(
            """
            INSERT INTO person_group_roles (id, person_id, group_id, role_type)
            VALUES (:id, :person_id, :group_id, :role_type)
            """
        ),
        _PERSON_GROUP_ROLES,
    )
    await _sync_sequence(session, "person_group_roles")
    await session.commit()


async def reset_and_seed_defaults(session: AsyncSession) -> None:
    await reset_seeded_db(session)
    await seed_location_nodes(session)
    await seed_group_nodes(session)
    await seed_equipment_types(session)
    await seed_departments(session)
    await seed_persons(session)
    await seed_person_group_roles(session)


async def ensure_seed_defaults(session: AsyncSession) -> bool:
    if not await is_seed_data_missing(session):
        return False

    await seed_location_nodes(session)
    await seed_group_nodes(session)
    await seed_equipment_types(session)
    await seed_departments(session)
    await seed_persons(session)
    await seed_person_group_roles(session)
    return True
