import datetime as dt
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup as bs
from sqlalchemy import Index
from sqlalchemy.exc import ProgrammingError

import src
from src import ppCleaner as ppc
from src.models import Article, Base, Newsroom, Newsroom_visit
from src.ppSplitter import split_articles_and_add_reports_to_db
from src import utils

import sys

DATA_FOLDER_NAME = "ppp_bw"
INIT = sys.argv[1]  # str -> if 'init', db will be initialized from scratch
YEAR = sys.argv[2]  # int -> provide the year


def import_newsroom_legacy_data(legacy_data_path, engine):
    """
    Imports legacy csv files of newrooms to database
    """
    folder_path = Path.joinpath(legacy_data_path, "departments")

    list_of_dfs = []
    for f in Path(folder_path).iterdir():
        df = pd.read_csv(Path.joinpath(folder_path, f.name))
        list_of_dfs.append(df)

    df_all = pd.concat(list_of_dfs, ignore_index=False)
    df_all = df_all.rename(
        columns={
            "newsroom_title": "title",
            "newsroom_subtitle": "subtitle",
            "name_of_dept": "dept_name",
            "district_of_dept": "dept_district",
            "state_of_dept": "dept_state",
            "newsroom_link": "link",
            "newsroom_weblinks": "weblinks",
        }
    )

    df_all = df_all.drop_duplicates(
        subset=df_all.columns.difference(["scraping_datetime"])
    )
    df_all = df_all.sort_values(by="newsroom_nr")
    df_all.reset_index(inplace=True, drop=True)
    df_all.index = df_all.index + 1

    df_visits = df_all[["scraping_datetime"]].copy()
    df_visits["newsroom_id"] = df_visits.index

    df_all.drop(columns=["scraping_datetime"], inplace=True)

    df_all.to_sql(name="newsrooms", con=engine, if_exists="append", index=False)
    df_visits.to_sql(
        name="newsroom_visits", con=engine, if_exists="append", index=False
    )


def parse_newsroom(state, year, newsroom, legacy_data_path):
    global engine, Session
    session = Session()

    # create logbook
    logbook = utils.Logbook(legacy_data_path, "errorlog_article_import_" + utils.get_str_dt() + ".log")

    # check if newsroom already in db (obesolete?)
    room = session.query(Newsroom).filter_by(newsroom_nr=newsroom.name).one_or_none()
    if not room:
        room = Newsroom(
            newsroom_nr=newsroom.name,
        )
        session.add(room)

    for file in newsroom.iterdir():

        # Only access .txt files
        if not file.suffix == ".txt":
            continue

        # Check if Article is already in db
        article_file = (
            session.query(Article)
            .filter_by(article_file=str(file.relative_to(legacy_data_path)))
            .one_or_none()
        )

        # If Article in db, then  skip
        if article_file:
            logbook.write_entry(" already in db: " + str(file))
            print("file already in db...")
            continue
    
        if not article_file:
            try:
                newsroom_nr, published, i, crawled = file.name.rstrip(".txt").split("_")

                published = dt.datetime.strptime(published, "%Y-%m-%d")
                crawled = dt.datetime.strptime(crawled, "%Y-%m-%d-%H-%M-%S")

                content = file.read_text(encoding="utf-8")

                html = bs(content, "html.parser")

                article_data = ppc.extract_article_data(html, newsroom_nr)

                article = Article(
                    date=published,
                    scraped_at=crawled,
                    daily_index=i,
                    article_link=article_data["article_link"],
                    article_file=str(file.relative_to(legacy_data_path)),
                    newsroom_nr=newsroom_nr,
                    location=article_data["location"],
                    header=article_data["header"],
                    text=article_data["text"],
                    location_tags_names=article_data["location_tags_names"],
                    location_tags_scores=article_data["location_tags_scores"],
                    topic_tags_names=article_data["topic_tags_names"],
                    topic_tags_scores=article_data["topic_tags_scores"],
                )
                article.newsroom = room
                article.newsroom_visit = (
                    session.query(Newsroom_visit)
                    .filter_by(newsroom_id=room.id)
                    .one_or_none()
                )
                session.add(article)
                split_articles_and_add_reports_to_db(article, session)
                session.commit()

            except:
                logbook.write_entry(" error importing: " + str(file))
                print("Error...")

    session.close()


def add_final_indexes():
    global engine

    indexes = [
        Index("article_newsroom_ix", Article.newsroom_id),
        Index("article_date_ix", Article.date),
    ]

    for index in indexes:
        try:
            index.create(bind=engine)
        except ProgrammingError:
            pass


def import_article_legacy_data(legacy_data_path):
    archived_html_path = Path.joinpath(legacy_data_path, "articles", "raw_article_html")

    for state in Path(archived_html_path).iterdir():
        print("Importing state: ", state.name)
        for year in state.iterdir():
            if year.name != YEAR:
                continue

            print("Importing year: ", year.name)
            for newsroom in year.iterdir():
                parse_newsroom(state, year, newsroom, legacy_data_path)


def main():
    legacy_data_path = Path.joinpath(src.PATH, "output_data", DATA_FOLDER_NAME)

    if INIT=="init":
        # Drops and recreates DB
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(bind=engine)

        import_newsroom_legacy_data(legacy_data_path, engine)

    import_article_legacy_data(legacy_data_path)
    # add_final_indexes()


if __name__ == "__main__":
    engine, Session = src.db_connection(init=False)
    main()
    engine.dispose()
