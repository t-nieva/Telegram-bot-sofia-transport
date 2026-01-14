from dataclasses import dataclass
from typing import Optional


@dataclass
class RealtimeArrival:
    trip_id: str
    stop_id: str
    arrival_time: Optional[int]  # unix timestamp
    delay: Optional[int]
