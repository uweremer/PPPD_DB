import logging

import spacy
from spacy.matcher import PhraseMatcher

from src.geo2txt.models import Geoname, Related_Text
from src.models import Report


def get_geonames(session):
    '''
    Get geonames for Phrase Matcher and Lookup
    Only subset for populated places in Baden-Württemberg
    '''

    #session = Session()
    logging.debug('Retrieving populated places geonames from db...')
    geonames = (
        session.query(Geoname)
        .filter((Geoname.feature_class == "A") | (Geoname.feature_class == "P"))
        .filter(Geoname.admin4_code.like("08%"))
    )
    logging.info('%s geonames queried from db...', geonames.count())
    return geonames


def build_phrase_matcher_pipeline(geonames):
    logging.debug('Building PhraseMatcher pipeline...')

    nlp = spacy.load('de_core_news_sm')
    # First, feed Phrase Matcher with Geonames
    matcher = PhraseMatcher(nlp.vocab)

    terms = []
    for geoname in geonames:
        terms.append(geoname.name)

    # Only run nlp.make_doc to speed things up
    patterns = [nlp.make_doc(text) for text in set(terms)]
    matcher.add("TerminologyList", None, *patterns)

    logging.info('PhraseMatcher succesfully prepared...')
    return nlp, matcher


def topo_extract(text, nlp, matcher):
    '''
    Expects a text snippet, returns a list
    of matched toponyms or null.
    '''

    doc = nlp(text)
    matches = matcher(doc)

    topo_list = []
    for match_id, start, end in matches:
        topo_list.append(doc[start:end].text)

    return (topo_list)


def text_toponym_lookup(text, geonames, nlp, matcher, session, report_id, **kwargs):
    '''
    Expects entities and performs lookup in Geonames
    table. Returns a unique set of Geoname queries
    with preference for ADM4 units. Has additioanl
    keyword arguments `singular` (defaults to False),
    which forces to return a single toponym (the
    smallest possible unit).
    Additioanl keyword arguments `report_id`
    and `session`.
    '''

    topo_list = topo_extract(text, nlp, matcher)
    matched_topo_list = []
    for topo in topo_list:
        lookup_query = geonames.where(Geoname.name == topo)
        if not lookup_query.count() > 0:
            lookup_query = geonames.where(Geoname.name.startswith(topo))

        lookup_query_ppl = lookup_query.where(Geoname.feature_code == "PPL")
        if lookup_query_ppl.count() > 0:
            lookup_query = lookup_query_ppl

        for topo in lookup_query:
            matched_topo_list.append(topo)

    # Push to DB
    for topo in set(matched_topo_list):
        rel_text = Related_Text(foreign_text_id=report_id,
                                related_geonames=[topo])
        session.add(rel_text)
        session.commit()

    # Show results and return unique queryset
    if kwargs.get('verbose') is True:
        print(text)
        for topo in set(matched_topo_list):
            print(topo.name, topo.admin4_code, topo.feature_code)
        print("\n*******************************\n")

    logging.debug('%s toponyms extracted...', len(set(matched_topo_list)))
    return (set(matched_topo_list))


def bulk_text_toponym_lookup(Session, start_after, end):
    logging.info("Starting bulk_text_toponym_lookup...")
    session = Session()
    geonames = get_geonames(session)
    nlp, matcher = build_phrase_matcher_pipeline(geonames)
    reports = session.query(Report).order_by(Report.id).slice(start_after, end)
    for r in reports:
        text_toponym_lookup(
            r.text_snippet,
            geonames,
            nlp,
            matcher,
            session,
            report_id=r.id,
            verbose=False,
        )
    session.close()
    logging.info("bulk_text_toponym_lookup finished...")
