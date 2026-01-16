"""
GTFS parser module.

Responsible for extracting the GTFS ZIP archive and preparing
the directory with CSV files for further validation and processing.
"""

import zipfile
from pathlib import Path


class GTFSParser:
    def __init__(self, zip_path: Path, extract_dir: Path):
        self.zip_path = zip_path
        self.extract_dir = extract_dir

    def extract(self) -> bool:
        try:
            self.extract_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(self.zip_path, "r") as z:
                z.extractall(self.extract_dir)

            print(f"GTFS extracted to: {self.extract_dir}")
            return True

        except Exception as e:
            print(f"GTFS extraction failed: {e}")
            return False
