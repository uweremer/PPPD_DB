import datetime
import pickle

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

import src
from src.functions import bulk_preprocessing

engine, Session = src.db_connection(init=False)


#### WORK IN PROGRESS

start = datetime.datetime.now()

#df1 = bulk_preprocessing(Session, start_after=0, ends_with=150000)
#df2 = bulk_preprocessing(Session, start_after=150000, ends_with=350000)
#df3 = bulk_preprocessing(Session, start_after=350000, ends_with=526661)
#df = bulk_preprocessing(Session)

diff = datetime.datetime.now() - start
print(diff)

#pickle.dump(df1, open("preprocessed_reports_1.pkl", 'wb'))
#pickle.dump(df2, open("preprocessed_reports_2.pkl", 'wb'))
#pickle.dump(df3, open("preprocessed_reports_3.pkl", 'wb'))


# Open an d push to db
files = ["preprocessed_reports_1.pkl", 
         "preprocessed_reports_2.pkl", 
         "preprocessed_reports_3.pkl" ]

def push_to_db(files):
    i = 1
    for f in files:
        print(i)
        file = open(f,'rb')
        df = pickle.load(file)
        df = df.drop(columns=['normalised_text', 'nlp_text'])
        df.head()
        df.to_sql("corpus", con=engine, if_exists="append", index=False)
        i += 1
push_to_db(files)
# note: DB table modiefied to excluded text_snippet



# Generator for db retrieval of lemmas
# def get_lemmas():
#     for i in range(0, 526661, 10000):
#         print(i)
#         query = "SELECT lemmas FROM corpus LIMIT 10000 OFFSET " + str(i)
#         df = pd.read_sql(query, con=engine)
#         for doc in df['lemmas'].values:
#             yield doc

# corpus = get_lemmas()
# vectorizer = TfidfVectorizer(max_features=5000)
# vectorizer.fit(corpus)

# Altes Vocab laden
vectorizer = pickle.load(open("./output_data/relevance_classifier/vocab.pkl", "rb" ))

# train_x = vectorizer.transform(corpus) Warum geht der generator hier nicht?
query = "SELECT * FROM corpus"
df = pd.read_sql(query, con=engine)
train_x = vectorizer.transform(df['lemmas'])
train_x

# Altes Modell laden
grid = pickle.load(open("./output_data/relevance_classifier/final_svm.pkl", "rb" ))
grid_pred = grid.predict(train_x)
sum(grid_pred)/len(grid_pred)

df["relevanz"] = grid_pred
#df["report_id"] = df.reset_index().index
df.head()

df.to_csv("20230913_ppp_predictions.csv",
          encoding='UTF-8',
          index=False)


df.drop(columns=['text_snippet','lemmas']).to_sql("predictions", con=engine, if_exists="append", index=False)