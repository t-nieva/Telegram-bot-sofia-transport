from datetime import datetime, timedelta, timezone
from transport.models.stop_info import StopInfo, Arrival
from transport.constants import SOFIA_TZ


class TransportService:
    def __init__(self, static_gtfs, realtime_gtfs):
        self.static = static_gtfs
        self.realtime = realtime_gtfs

    def get_stop_info(self, stop_code: str) -> StopInfo:
        stop = self.static.get_stop_by_code(stop_code)
        if not stop:
            raise ValueError(f"Stop with code {stop_code} not found")

        now = datetime.now(SOFIA_TZ)

        stop_times = self.static.get_stop_times(stop.stop_id)
        realtime_index = self.realtime.get_realtime_index()

        arrivals = []

        for st in stop_times:
            # статическое время (локальное)
            static_arrival = self.static._parse_gtfs_time(st.arrival, now.date())

            trip = self.static.trips.get(st.trip_id)
            route = self.static.routes.get(trip.route_id)

            # realtime override
            rt = realtime_index.get((st.trip_id, st.stop_id))

            if rt:
                if rt["arrival_time"]:
                    arrival_dt = rt["arrival_time"]  # уже локальное
                elif rt["delay"]:
                    arrival_dt = static_arrival + timedelta(seconds=rt["delay"])
                else:
                    arrival_dt = static_arrival
            else:
                arrival_dt = static_arrival

            if arrival_dt < now:
                continue

            minutes_left = int((arrival_dt - now).total_seconds() // 60)

            arrivals.append(
                Arrival(
                    route_number=route.short_name,
                    arrival_time=arrival_dt,
                    minutes_left=minutes_left,
                )
            )

        # arrivals.sort(key=lambda a: a.arrival_time)
        # arrivals = arrivals[:5]

        # --- Оставляем только ближайшее прибытие для каждого маршрута ---
        unique_by_route = {}

        for a in arrivals:
            if a.route_number not in unique_by_route:
                unique_by_route[a.route_number] = a
            else:
                # если уже есть — оставляем более раннее прибытие
                if a.arrival_time < unique_by_route[a.route_number].arrival_time:
                    unique_by_route[a.route_number] = a

        # превращаем обратно в список
        arrivals = list(unique_by_route.values())

        # сортируем по времени прибытия
        arrivals.sort(key=lambda a: a.arrival_time)

        return StopInfo(
            stop_code=stop.stop_code,
            stop_name=stop.name,
            current_time=now,
            arrivals=arrivals,
        )
