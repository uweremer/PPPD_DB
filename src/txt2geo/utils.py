import datetime
import os
import zipfile
from pathlib import Path

import pandas as pd
import requests

import src

import logging
from sqlalchemy import exc


def get_geonames_and_populate_db(engine):
    """
    Imports the record of the geonames data and pushes them to the db

    Source: http://download.geonames.org/export/dump/DE.zip
    """

    # Download Geonames data and unzip
    if not Path(Path.joinpath(src.PATH, "external_data", "DE.txt")).is_file():
        url = "http://download.geonames.org/export/dump/DE.zip"
        logging.debug('Downloading geonames data from %s', url)
        r = requests.get(url)
        with open(Path.joinpath(src.PATH, "external_data", "DE.zip"), "wb") as f:
            f.write(r.content)
        with zipfile.ZipFile(
            Path.joinpath(src.PATH, "external_data", "DE.zip"), "r"
        ) as f:
            f.extractall(Path.joinpath(src.PATH, "external_data"))
        os.remove(Path(Path.joinpath(src.PATH, "external_data", "DE.zip")))

    # Not all columns from the GV file are relevant.
    # Here we define which columns are imported
    cols = list(range(0, 15))
    cols.append(18)

    # Labels for the columns
    names = [
        "id",
        "name",
        "asciiname",
        "alternatenames",
        "latitude",
        "longitude",
        "feature_class",
        "feature_code",
        "country_code",
        "cc2",
        "admin1_code",
        "admin2_code",
        "admin3_code",
        "admin4_code",
        "population",
        "modification_date",
    ]

    # Data type for the columns
    dtype = {
        "id": int,
        "name": str,
        "asciiname": str,
        "alternatenames": str,
        "latitude": float,
        "longitude": float,
        "feature_class": str,
        "feature_code": str,
        "country_code": str,
        "cc2": str,
        "admin1_code": str,
        "admin2_code": str,
        "admin3_code": str,
        "admin4_code": str,
        "population": float,
        "modification_date": str,
    }

    # Actual import of the file
    geonames_file = Path.joinpath(src.PATH, "external_data", "DE.txt")
    logging.debug('Reading geonames from file: %s', str(geonames_file))
    data = pd.read_csv(
        geonames_file,
        sep="\t",
        header=None,
        usecols=cols,
        dtype=dtype,
        names=names,
    )

    for column in data:
        if data[column].dtypes == "float64":
            data[column] = data[column].fillna(-1)
        if data[column].dtypes == "str":
            data[column] = data[column].apply(lambda i: i or None)
  
    try:
        logging.debug('Pushing geonames to database...')
        data.to_sql(name="geonames", con=engine, if_exists="append", index=False)
        logging.info('Geonames imported to database...')
    except exc.IntegrityError as e:
        logging.warning(e)
        pass

    logging.info("Created db table for geonames...")