import urllib.request
import zipfile
from pathlib import Path

from constants import GTFS_URL


class StaticGTFS:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.data_dir = self.project_root / "data"
        self.zip_path = self.data_dir / "gtfs.zip"
        self.gtfs_path = self.data_dir / "gtfs"

    def _ensure_gtfs_downloaded(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.zip_path.exists():
            urllib.request.urlretrieve(GTFS_URL, self.zip_path)

        if not self.gtfs_path.exists():
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                zip_ref.extractall(self.gtfs_path)
