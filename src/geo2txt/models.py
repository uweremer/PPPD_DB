from typing import List
from typing import Optional
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass

class Geoname(Base):
    __tablename__ = "geonames"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    asciiname: Mapped[Optional[str]]
    fullname: Mapped[Optional[str]]
    alternatenames: Mapped[Optional[str]]
    latitude: Mapped[Optional[float]]
    longitude: Mapped[Optional[float]]
    feature_class: Mapped[Optional[str]]
    feature_code: Mapped[Optional[str]]
    country_code: Mapped[str]
    cc2: Mapped[Optional[str]]
    admin1_code: Mapped[Optional[str]]
    admin2_code: Mapped[Optional[str]]
    admin3_code: Mapped[Optional[str]]
    admin4_code: Mapped[Optional[str]]
    population: Mapped[Optional[float]]
    modification_date: Mapped[Optional[str]]

    def __repr__(self) -> str:
        return f"Geoname(name={self.name!r}, id={self.id!r})"
