import pandas as pd
import os

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from surprise import Reader, Dataset, dump, KNNBasic
from surprise.model_selection import cross_validate

from Config import DB
engine=DB().DB_Engine()

import warnings
warnings.filterwarnings('ignore')

def read_files():
         interaction=pd.read_sql(
         """WITH combined_data AS ( 
         SELECT user_id, event_id 
         FROM likes 
         UNION ALL 
         SELECT user_id, event_id 
         FROM event_interest 
         ) 
         SELECT DISTINCT user_id, event_id 
         FROM combined_data;""",engine)

         events=pd.read_sql("SELECT event_id,category FROM event_categories",engine)
         events=events[events.category!="Other"]
         events=events.groupby('event_id')['category'].apply(' '.join).reset_index()

         users=pd.read_sql("SELECT user_id,category FROM user_category",engine)
         users=users[users.category!="Other"]
         users=users.groupby('user_id')['category'].apply(' '.join).reset_index()
                
         def content_based():
                     events_count_matrix = CountVectorizer(min_df=0.0,analyzer='word',ngram_range=(1,5),stop_words='english')
                     events_count=events_count_matrix.fit_transform(events['category'])

                     users_count_matrix = CountVectorizer(vocabulary=events_count_matrix.get_feature_names_out())
                     users_count=users_count_matrix.fit_transform(users['category'])

                     user_cs=cosine_similarity(users_count,events_count)
                     user_cs=pd.DataFrame(user_cs).set_index(users['user_id'].astype(str))
                     user_cs.columns=events['event_id']
                     user_cs=user_cs.T

                     event_cs = cosine_similarity(events_count)
                     event_cs=pd.DataFrame(event_cs).set_index(events['event_id'].astype(str))
                     event_cs.columns=events['event_id']
                     event_cs=event_cs.T

                     event_cs.to_sql(name='event_cs',con=engine,if_exists='replace',index=True)
                     user_cs.to_sql(name='user_cs',con=engine,if_exists='replace',index=True)
         def collaborative_filtering():
                  interaction.drop_duplicates(inplace=True)
                  interaction['interaction']=1
                  
                  reader = Reader()
                  data = Dataset.load_from_df(interaction, reader)

                  sim_options = {"name": "cosine","user_based": True}
                  knn = KNNBasic(sim_options=sim_options,verbose=False,random_state=42)

                  cross_validate(knn, data, measures=['RMSE', 'MAE'],cv=5)

                  trainset = data.build_full_trainset()
                  trainset.rating_scale=(0,1)
                  knn.fit(trainset)

                  file_name = os.path.expanduser("./collaborative_model.pkl")
                  dump.dump(file_name, algo=knn)
         return content_based(),collaborative_filtering()

read_files()

