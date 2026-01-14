import csv
import urllib.request
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, date, time, timedelta
from zoneinfo import ZoneInfo

from transport.models.static.gtfs_models import Stop, StopTime, Route, Trip
from transport.models.stop_info import Arrival, StopInfo
from transport.constants import GTFS_URL


class StaticGTFS:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.data_dir = self.project_root / "data"
        self.zip_path = self.data_dir / "gtfs.zip"
        self.gtfs_path = self.data_dir / "gtfs"

        # Main tables
        self.stops: Dict[str, Stop] = {}
        self.routes: Dict[str, Route] = {}
        self.trips: Dict[str, Trip] = {}
        self.stop_times: List[StopTime] = []

        # Indexes
        self.stop_code_index: Dict[str, str] = {}
        self.stop_times_by_stop: Dict[str, List[StopTime]] = {}
        self.stop_times_by_trip: Dict[str, List[StopTime]] = {}

    def load(self):
        self._ensure_gtfs_downloaded()
        self._load_stops()
        self._load_routes()
        self._load_trips()
        self._load_stop_times()
        self._build_indexes()

    def _ensure_gtfs_downloaded(self):
        self.data_dir.mkdir(parents=True, exist_ok=True)

        if not self.zip_path.exists():
            urllib.request.urlretrieve(GTFS_URL, self.zip_path)

        if not self.gtfs_path.exists():
            with zipfile.ZipFile(self.zip_path, "r") as zip_ref:
                zip_ref.extractall(self.gtfs_path)

    # CSV download
    def _load_stops(self):
        path = self.gtfs_path / "stops.txt"
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                stop = Stop(
                    stop_id=row["stop_id"],
                    stop_code=row.get("stop_code"),
                    name=row["stop_name"],
                    lat=float(row["stop_lat"]),
                    lon=float(row["stop_lon"]),
                )
                self.stops[stop.stop_id] = stop
                if stop.stop_code:
                    self.stop_code_index[stop.stop_code] = stop.stop_id

    def _load_routes(self):
        path = self.gtfs_path / "routes.txt"
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.routes[row["route_id"]] = Route(
                    route_id=row["route_id"],
                    short_name=row["route_short_name"],
                    long_name=row["route_long_name"],
                )

    def _load_trips(self):
        path = self.gtfs_path / "trips.txt"
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.trips[row["trip_id"]] = Trip(
                    trip_id=row["trip_id"],
                    route_id=row["route_id"],
                    service_id=row["service_id"],
                    headsign=row.get("trip_headsign"),
                )

    def _load_stop_times(self):
        path = self.gtfs_path / "stop_times.txt"
        with open(path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                st = StopTime(
                    trip_id=row["trip_id"],
                    stop_id=row["stop_id"],
                    arrival=row["arrival_time"],
                    departure=row["departure_time"],
                    sequence=int(row["stop_sequence"]),
                )
                self.stop_times.append(st)

    def _build_indexes(self):
        for st in self.stop_times:
            self.stop_times_by_stop.setdefault(st.stop_id, []).append(st)
            self.stop_times_by_trip.setdefault(st.trip_id, []).append(st)

        for trip_id in self.stop_times_by_trip:
            self.stop_times_by_trip[trip_id].sort(key=lambda x: x.sequence)

    # API
    def get_stop_by_code(self, stop_code: str) -> Optional[Stop]:
        stop_id = self.stop_code_index.get(stop_code)
        return self.stops.get(stop_id)

    def get_stop_times(self, stop_id: str) -> List[StopTime]:
        return self.stop_times_by_stop.get(stop_id, [])

    @staticmethod
    def _parse_gtfs_time(t: str, d: date, tz=ZoneInfo("Europe/Sofia")) -> datetime:
        hh, mm, ss = map(int, t.split(":"))
        base = datetime.combine(d, time(0, 0, 0), tzinfo=tz)
        return base + timedelta(hours=hh, minutes=mm, seconds=ss)

    def get_stop_info_by_code(self, stop_code: str) -> Optional[StopInfo]:
        now = datetime.now(ZoneInfo("Europe/Sofia"))
        arrivals: List[Arrival] = []
        stop = self.get_stop_by_code(stop_code)
        if not stop:
            return None

        stop_times = self.get_stop_times(stop.stop_id)
        for st in stop_times:
            arrival_dt = self._parse_gtfs_time(st.arrival, now.date())
            if arrival_dt < now:
                continue

            trip = self.trips.get(st.trip_id)
            if not trip:
                continue

            route = self.routes.get(trip.route_id)
            if not route:
                continue

            minutes_left = int((arrival_dt - now).total_seconds() // 60)

            arrivals.append(
                Arrival(
                    route_number=route.short_name,
                    arrival_time=arrival_dt,
                    minutes_left=minutes_left,
                )
            )

        arrivals.sort(key=lambda a: a.arrival_time)
        arrivals = arrivals[:5]

        return StopInfo(
            stop_code=stop.stop_code,
            stop_name=stop.name,
            current_time=now,
            arrivals=arrivals,
        )
