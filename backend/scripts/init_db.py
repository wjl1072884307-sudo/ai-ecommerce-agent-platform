import argparse
import sys
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.database import Base, SessionLocal, engine
from app.models import entities  # noqa: F401
from app.services.demo_seed import seed_demo_data


def init_database(reset: bool = False, seed: bool = True) -> None:
    if reset:
        Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    if seed:
        with SessionLocal() as db:
            seed_demo_data(db)


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize local SQLite database.")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate all tables.")
    parser.add_argument("--no-seed", action="store_true", help="Create tables without demo data.")
    args = parser.parse_args()

    init_database(reset=args.reset, seed=not args.no_seed)
    print("Database initialized successfully.")


if __name__ == "__main__":
    main()
