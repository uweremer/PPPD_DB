import argparse
import logging
from pathlib import Path

import src
import src.txt2geo
from src.txt2geo.geolocator import bulk_text_toponym_lookup
from src.txt2geo.models import Base
from src.txt2geo.utils import get_geonames_and_populate_db


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--log",
        dest="LOGLEVEL",
        type=str,
        default="WARNING",
        help="Set logging level, defaults to: WARNING",
    )
    parser.add_argument(
        "--init",
        dest="INITIALIZE",
        type=int,
        default=0,
        help="Initialize tables in database: 1=yes, 0=no (default)",
    )
    parser.add_argument(
        "--start_after",
        dest="START_AFTER",
        type=int,
        default=None,
        help="Set limit of batch for bulk toponym lookup - starts after this report ID.",
    )
    parser.add_argument(
        "--ends_with",
        dest="ENDS_WITH",
        type=int,
        default=None,
        help="Set limit of batch for bulk toponym lookup - ends with this report ID.",
    )
    parser.add_argument(
        "--increment",
        dest="INCREMENT",
        type=int,
        default=None,
        help="Set upper limit of batch for bulk toponym lookup by providing an increment.",
    )

    args = parser.parse_args()
    
    if (args.ENDS_WITH is not None) & (args.INCREMENT is not None):
        parser.error('--ends_with and --increment may not be used simultaneusly!\n Use --help for more information.')
    
    
    numeric_level = getattr(logging, args.LOGLEVEL.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError("Invalid log level: %s" % args.LOGLEVEL)
    log_path = Path.joinpath(src.PATH, "output_data", "logs")
    log_path.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        filename=Path.joinpath(log_path, "txt2geo.log"),
        filemode="a",  # w for fresh file on every run
        level=numeric_level,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    engine, Session = src.db_connection(init=False)

    if args.INITIALIZE == 1:
        logging.info('Start initializing db tables for geolocation.')
        Base.metadata.tables["geonames"].create(bind=engine, checkfirst=True)
        Base.metadata.tables["related_texts"].create(bind=engine, checkfirst=True)
        Base.metadata.tables["association_table"].create(bind=engine, checkfirst=True)
        get_geonames_and_populate_db(engine)
    if args.INITIALIZE == 0:
        logging.info('Skipping initializing db tables for geolocation.')
        
    if args.INCREMENT:
        ends_with = args.START_AFTER + args.INCREMENT
    if args.ENDS_WITH:
        ends_with = args.ENDS_WITH
        
    bulk_text_toponym_lookup(Session,
                             start_after=args.START_AFTER,
                             ends_with=ends_with)  # takes a while
    engine.dispose()


if __name__ == "__main__":
    main()
