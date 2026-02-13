from __future__ import annotations

from pathlib import Path
import duckdb


DB_PATH = Path("warehouse/hospital_ops.duckdb")
SQL_PATH = Path("sql/create_gold_tables.sql")


def main() -> None:
    if not SQL_PATH.exists():
        raise FileNotFoundError(f"SQL script not found: {SQL_PATH}")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))

    sql_script = SQL_PATH.read_text(encoding="utf-8")

    con.execute(sql_script)
    con.close()

    print("✅ Gold layer built successfully")
    print(f"Saved DuckDB database to: {DB_PATH}")


if __name__ == "__main__":
    main()
