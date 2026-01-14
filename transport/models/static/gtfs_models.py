from dataclasses import dataclass
from typing import Optional


@dataclass
class Stop:
    stop_id: str
    stop_code: str | None
    name: str
    lat: float
    lon: float


@dataclass
class StopTime:
    trip_id: str
    stop_id: str
    arrival: str
    departure: str
    sequence: int


@dataclass
class Route:
    route_id: str
    short_name: str
    long_name: str


@dataclass
class Trip:
    trip_id: str
    route_id: str
    service_id: str
    headsign: Optional[str]
