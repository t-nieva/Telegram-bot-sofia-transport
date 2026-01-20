from pathlib import Path
from transport.static_gtfc.downloader import GTFSDownloader
from transport.static_gtfc.parser import GTFSParser
from transport.static_gtfc.validator import GTFSValidator
from transport.static_gtfc.importer import GTFSImporter
from transport.constants import GTFS_URL


class GTFSService:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.data_dir = self.project_root / "data"
        self.zip_path = self.data_dir / "gtfs.zip"
        self.gtfs_path = self.data_dir / "gtfs"

    def update(self) -> bool:
        # 1. Download
        downloader = GTFSDownloader(url=GTFS_URL, save_zip_path=self.zip_path)
        if not downloader.download():
            return False
        # 2. Extract
        parser = GTFSParser(
            zip_path=downloader.save_zip_path,
            extract_dir=self.gtfs_path,
        )
        if not parser.extract():
            return False
        # 3. Validate
        validator = GTFSValidator(extract_dir=self.gtfs_path)
        if not validator.validate():
            return False

        # 4. Import into DB
        importer = GTFSImporter(extract_dir=self.gtfs_path)
        if not importer.import_data():
            print("GTFS import failed")
            return False
        print("GTFS update completed successfully")
        return True
