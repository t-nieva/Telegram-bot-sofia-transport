from datetime import datetime, timezone
import requests
from google.transit import gtfs_realtime_pb2
from transport.constants import TRIP_UPDATES_URL, SOFIA_TZ


class RealtimeGTFS:
    def fetch_trip_updates(self):
        response = requests.get(TRIP_UPDATES_URL)
        feed = gtfs_realtime_pb2.FeedMessage()
        feed.ParseFromString(response.content)
        return feed

    def get_realtime_index(self):
        """
        Возвращает словарь:
        {(trip_id, stop_id): {"arrival_time": datetime|None, "delay": int|None}}
        """
        feed = self.fetch_trip_updates()
        index = {}

        for entity in feed.entity:
            if not entity.HasField("trip_update"):
                continue

            trip_update = entity.trip_update
            trip_id = trip_update.trip.trip_id

            for stu in trip_update.stop_time_update:
                stop_id = stu.stop_id

                arrival_time = (
                    datetime.fromtimestamp(
                        stu.arrival.time, tz=timezone.utc
                    ).astimezone(SOFIA_TZ)
                    if stu.arrival.HasField("time")
                    else None
                )

                delay = stu.arrival.delay if stu.arrival.HasField("delay") else None

                index[(trip_id, stop_id)] = {
                    "arrival_time": arrival_time,
                    "delay": delay,
                }

        return index
