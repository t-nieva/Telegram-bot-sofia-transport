from transport.static.static_gtfs import StaticGTFS
from transport.realtime.realtime_gtfs import RealtimeGTFS
from transport.services.transport_service import TransportService


# инициализации зависимостей (dependency injection)
def create_transport_service() -> TransportService:
    static_gtfs = StaticGTFS()
    static_gtfs.load()  # 🔴 важно — грузим ОДИН раз

    realtime_gtfs = RealtimeGTFS()

    return TransportService(
        static_gtfs=static_gtfs,
        realtime_gtfs=realtime_gtfs,
    )
