from __future__ import annotations

from typing import Optional, List

from sqlalchemy import Column, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models import Base


geo2text_association_table = Table(
    "association_table",
    Base.metadata,
    Column("geonames_id", ForeignKey("geonames.id"), primary_key=True),
    Column("related_texts_id", ForeignKey("related_texts.id"), primary_key=True),
)


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

    related_texts: Mapped[List[Related_Text]] = relationship(
        secondary=geo2text_association_table, back_populates="related_geonames"
    )

    def __repr__(self) -> str:
        return f"Geoname(name={self.name!r}, admin4_code={self.admin4_code!r}, id={self.id!r})"


class Related_Text(Base):
    __tablename__ = "related_texts"

    id: Mapped[int] = mapped_column(primary_key=True)
    foreign_text_id: Mapped[int]  # = mapped_column(ForeignKey("reports.id"))

    related_geonames: Mapped[List[Geoname]] = relationship(
        secondary=geo2text_association_table, back_populates="related_texts"
    )
