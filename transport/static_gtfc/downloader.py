"""
GTFS downloader module.

This module is responsible for downloading the GTFS ZIP archive
from the configured URL and saving it to the local data directory.
"""

import requests
from pathlib import Path


class GTFSDownloader:
    def __init__(self, url: str, save_zip_path: Path):
        self.url = url
        self.save_zip_path = save_zip_path

    def download(self) -> bool:
        try:
            self.save_zip_path.parent.mkdir(parents=True, exist_ok=True)
            response = requests.get(self.url)
            response.raise_for_status()
            with open(self.save_zip_path, "wb") as f:
                f.write(response.content)
                print(f"GTFS downloaded to: {self.save_zip_path}")
                return True
        except Exception as e:
            print(f"GTFS download failed: {e}")
            return False
