import src

from .models import Base
from .utils import get_geonames_and_populate_db

engine, Session = src.db_connection(init=False)
Base.metadata.tables["geonames"].create(bind=engine, checkfirst=True)
get_geonames_and_populate_db(engine)
