from pydantic import BaseModel
from fastapi import FastAPI,Request
from typing import Optional

from surprise import dump
from os import getenv
import pandas as pd
import uvicorn
from sqlalchemy import text

from Config import DB,APIServer

engine=DB().DB_Engine()
event_cs=pd.read_sql('SELECT * FROM event_cs',engine,index_col='event_id')
user_cs=pd.read_sql('SELECT * FROM user_cs',engine,index_col='event_id')

_, knn = dump.load("collaborative_model.pkl")
setattr(knn,'default_prediction',lambda: 0)

def check_user_interaction(user_id, event_id):
         conn=engine.connect()
         query =f"WITH combined_data AS ( SELECT user_id, event_id FROM likes UNION ALL SELECT user_id, event_id FROM event_interest)SELECT EXISTS (SELECT 1 FROM combined_data WHERE user_id = {user_id} AND event_id = {event_id});"
         result=conn.execute(text(query), {"user_id": user_id, "event_id": event_id})
         # Fetch the result (which will be a single boolean value)
         exists = result.fetchone()[0]    
         conn.close()
         return exists

# can work on both event and user
def content_based_recommendations(id,input='user',k=10):    
        try:    
                if input == 'user':
                        sim_scores = zip(user_cs[str(id)].index, user_cs[str(id)])
                elif input == 'event':
                        sim_scores = zip(event_cs[str(id)].index, event_cs[str(id)])

                sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

                if input == 'event':
                        sim_scores.pop(0)

                return [i[0] for i in sim_scores[0:k]] #event_indices
         
        except:
                 print('Input id is invalid for User/Event, make sure id relative to content')


def get_recommended_events(user_id,k=10):#for user
    try:
        recommended_events=[]
        def prediction(event_id):
                pred=knn.predict(user_id,event_id)

                if pred.est!=0 and not check_user_interaction(user_id,event_id):
                        return pred.est,pred.details['actual_k']
                else:
                        return 0,0
        
        recommended_events=content_based_recommendations(user_id,k=15)

        estimation=list(map(prediction,recommended_events))
        events=[(ev,est) for ev,est in zip(recommended_events,estimation)]
        events=sorted(events, key=lambda x: x[1], reverse=True)[0:k]
        return [ev[0] for ev in events ]

    except:
            print('Input id is invalid for User/Event, make sure id relative to content')


app = FastAPI()
api= APIServer()

class scoringitem(BaseModel):
        elementid:int
        k: Optional[int] = 10
    

@app.post('/event/')
async def scoring_endpoint(request: Request, item: scoringitem):
        api.check_authority(request)
        return content_based_recommendations(int(item.elementid), input='event', k=int(item.k))


@app.post('/user/')
async def scoring_endpoint(request: Request, item:scoringitem):
        api.check_authority(request)
        return get_recommended_events(int(item.elementid),k=int(item.k))


if __name__ == '__main__':
        port=int(getenv("PORT",8000))
        uvicorn.run("recommender:app",host="localhost",port=port,reload=True)

