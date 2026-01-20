"""
GTFS importer using temporary tables for atomic updates.
"""

import csv
from pathlib import Path
from transport.db.connection import get_db_connection


class GTFSImporter:
    def __init__(self, extract_dir: Path):
        self.extract_dir = extract_dir

    def import_data(self) -> bool:
        try:
            conn = get_db_connection()

            with conn:
                with conn.cursor() as cur:
                    self._import_table(
                        cur,
                        table="stops",
                        columns=[
                            "stop_id",
                            "stop_code",
                            "stop_name",
                            "stop_lat",
                            "stop_lon",
                        ],
                        csv_file=self.extract_dir / "stops.txt",
                    )

                    self._import_table(
                        cur,
                        table="routes",
                        columns=["route_id", "route_short_name", "route_long_name"],
                        csv_file=self.extract_dir / "routes.txt",
                    )

                    self._import_table(
                        cur,
                        table="trips",
                        columns=["trip_id", "route_id", "service_id"],
                        csv_file=self.extract_dir / "trips.txt",
                    )

                    self._import_table(
                        cur,
                        table="stop_times",
                        columns=[
                            "trip_id",
                            "arrival_time",
                            "departure_time",
                            "stop_id",
                            "stop_sequence",
                        ],
                        csv_file=self.extract_dir / "stop_times.txt",
                    )

                    self._import_table(
                        cur,
                        table="calendar_dates",
                        columns=["service_id", "date", "exception_type"],
                        csv_file=self.extract_dir / "calendar_dates.txt",
                    )

            conn.close()
            print("GTFS import completed successfully")
            return True

        except Exception as e:
            print(f"GTFS import failed: {e}")
            return False

    def _import_table(self, cur, table: str, columns: list, csv_file: Path):
        tmp_table = f"{table}_tmp"

        # 1. Create temporary table
        cur.execute(f"DROP TABLE IF EXISTS {tmp_table};")
        cur.execute(f"CREATE TABLE {tmp_table} (LIKE {table} INCLUDING ALL);")

        # 2. Load CSV into temporary table
        with open(csv_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                cur.execute(
                    f"""
                    INSERT INTO {tmp_table} ({", ".join(columns)})
                    VALUES ({", ".join(["%s"] * len(columns))})
                    """,
                    [row[col] for col in columns],
                )

        # 3. Atomic replace
        cur.execute(f"TRUNCATE {table};")
        cur.execute(f"INSERT INTO {table} SELECT * FROM {tmp_table};")

        # 4. Recreate index (optional)
        cur.execute(f"DROP INDEX IF EXISTS idx_{table}_pk;")
        cur.execute(f"CREATE INDEX idx_{table}_pk ON {table} ({columns[0]});")

        # 5. Drop temporary table
        cur.execute(f"DROP TABLE {tmp_table};")
