import logging
import pandas as pd
import re
import src
from src.models import Report
from pathlib import Path
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer

def bulk_preprocessing(Session, start_after: int, ends_with: int):
    logging.info("Starting bulk_preprocessing...")

    def normalise(text):
        if text: 
            text = f''' {text.lower()} '''
            # remove all urls
            ulr_regexer = r"(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'.,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"
            
            text = re.sub(ulr_regexer, ' ', text)

            # km/h
            text= re.sub(r'km/h', 'kmh', text)

            
            # km/h
            text= re.sub(r'ﬂ', 'ß', text)
            text= re.sub(r'ë', 'e', text)
            text= re.sub(r'ê', 'e', text)
            text= re.sub(r'ç', 'c', text)
            
            # ca. circa zirka
            text = re.sub(r'\bca. |\bca\b|\bzirka\b', 'circa', text)

            # Keep only words and whitespace
            text = re.sub(r'[^\w\s\-]+|\d', ' ', text)

            # remove leading space
            text = re.sub(r'^\s', '', text)
            # remove " - "
            text = re.sub(r'[\s]+-[\s]+', ' ', text)
            
            # remove hyphens excet when in location names or certain words
            text = re.sub(r'-(?!mail|straße|platz|brücke|bike|württemberg|baden|content|wyhlen|hall|gmünd|neustadt|tiengen|schwenningen|königshofen|ehingen|mühlhofen|worblingen|kirchen|neuthard|\w*-(?=straße|platz|brücke))', ' ', text)
            
            # geonames with "Bad ..." as bigram
            text = re.sub(r'\bbad ', 'bad_', text)
            
            # remove all single characters
            text = re.sub(r'\b[A-Za-zÀ-ž]\b', '', text)
            
            # remove multiple blankspaces
            text = re.sub(r'[\s]+', ' ', text)
            
            # remove leading and trailing whitespacw
            text = text.strip()
            
            return text
        else:
            return None



    def import_geonames_to_df(filename):
        geonames_df = pd.read_csv(filename, sep=  "\t",
                                    dtype = str,
                                    names = [str(x) for x in range(19)])

        # Get all populated places
        geonames_df = geonames_df[geonames_df['6'].str.contains('P', na=False)]

        # Only municipalities from Baden-Wuerttemberg
        geonames_df = geonames_df[geonames_df['10'] == '01']

        # Normalise Names
        geonames_df['normalised_text'] = geonames_df['1'].apply(lambda x: normalise(x))
        
        return geonames_df


    filename=Path.joinpath(src.PATH, "external_data/DE.txt")
    geonames_df = import_geonames_to_df(filename)
    geonames_list = geonames_df['normalised_text'].tolist()
    specific = ["polizeipräsidium", "polizeipräsidiums", "polizeireviers", "polizeirevier", "polizeiposten", 
                "präsidium", "pressestelle", "polizei", "polizeidienststelle", "hinweis", "tel", "original-content", 
                "pp", "stab", "oe", "ots"]

    stopwords = specific + geonames_list
    pattern = "|".join(stopwords)

    def sw_removal(text: str) -> str:
        res = re.sub(rf'\b(?:{pattern})\b', '', text)
        return(res)

    session = Session()
    reports = session.query(Report).order_by(Report.id).slice(start_after, ends_with).statement
    #reports = session.query(Report).order_by(Report.id).statement
    df = pd.read_sql(reports, session.bind)
    session.close()

    df['normalised_text'] = df['text_snippet'].apply(lambda x: normalise(x))
    df['normalised_text'] = df['normalised_text'].apply(lambda x: sw_removal(x))

    sp = spacy.load('de_core_news_sm')

    df['nlp_text'] = ""
    i=0
    for doc in sp.pipe(df['normalised_text'], 
                        disable=['tok2vec', 'tagger', 'morphologizer', 'parser', 'ner', 'attribute_ruler'],
                        n_process=-1):
        df['normalised_text'][i] = doc
        print(i)
        i += 1

    df['lemmas'] = ""
    for i in range(len(df['normalised_text'])):
        print(i)
        df['lemmas'][i] = []
        for token in df['normalised_text'][i]:
            if not token.is_stop:
                if not (token.lemma_ == " ") | (token.lemma_ == "_") | (len(token.lemma_) <= 1):
                    df['lemmas'][i].append(token.lemma_)
        
        df['lemmas'][i] = str(df['lemmas'][i])
    
    logging.info("bulk_preprocessing finished...")
    
    return df
    