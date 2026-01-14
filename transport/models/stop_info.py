from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Arrival:
    route_number: str
    arrival_time: datetime
    minutes_left: int


@dataclass
class StopInfo:
    stop_code: str
    stop_name: str
    current_time: datetime
    arrivals: List[Arrival]
