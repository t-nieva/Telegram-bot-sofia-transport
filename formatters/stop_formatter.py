from transport.models.stop_info import StopInfo


def format_stop_info(info: StopInfo) -> str:
    lines = [
        f"Ищу расписание для остановки {info.stop_code}",
        f"🚏 {info.stop_name}",
        f"🕒 {info.current_time.strftime('%H:%M')}",
        "",
    ]

    if not info.arrivals:
        lines.append("❌ Нет данных о прибытии транспорта")
    else:
        for arrival in info.arrivals:
            lines.append(
                f"🚌 {arrival.route_number} — через {arrival.minutes_left} мин"
            )

    return "\n".join(lines)
