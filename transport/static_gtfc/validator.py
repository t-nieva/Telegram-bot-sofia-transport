"""
GTFS validation module.

Checks the presence of required GTFS files and logs validation errors.
"""

from pathlib import Path


class GTFSValidator:
    REQUIRED_FILES = {
        "stops.txt",
        "routes.txt",
        "trips.txt",
        "stop_times.txt",
        "calendar_dates.txt",
    }

    def __init__(self, extract_dir: Path):
        self.extract_dir = extract_dir

    def validate(self) -> bool:
        missing = []

        for filename in self.REQUIRED_FILES:
            file_path = self.extract_dir / filename
            if not file_path.exists():
                missing.append(filename)

        if missing:
            print("Validation error: missing required GTFS files:")
            for f in missing:
                print(f" - {f}")

            return False

        print("GTFS validation passed")
        return True
