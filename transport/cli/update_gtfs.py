import sys
import logging

from transport.services.gtfs_service import GTFSService


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


def main() -> int:
    logging.info("GTFS update started")

    service = GTFSService()
    success = service.update()

    if not success:
        logging.error("GTFS update failed")
        return 1

    logging.info("GTFS update finished successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
