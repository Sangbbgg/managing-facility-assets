import argparse
import asyncio

from app.core.database import AsyncSessionLocal
from app.core.seed import ensure_seed_defaults, reset_and_seed_defaults


async def _run(reset: bool) -> int:
    async with AsyncSessionLocal() as session:
        if reset:
            await reset_and_seed_defaults(session)
            print("Seed reset complete.")
            return 0

        changed = await ensure_seed_defaults(session)
        if changed:
            print("Missing seed data inserted.")
        else:
            print("Seed data already present.")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed default master data.")
    parser.add_argument("--reset", action="store_true", help="truncate seed tables first")
    args = parser.parse_args()
    return asyncio.run(_run(args.reset))


if __name__ == "__main__":
    raise SystemExit(main())
