import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
from jwt import decode, ExpiredSignatureError
from fastapi import HTTPException,Request

load_dotenv()

class DB():
         def __init__(self):
                  self.user=os.environ.get('POSTGRES_USER')
                  self.password=os.environ.get('POSTGRES_PASSWORD')
                  self.host=os.environ.get('POSTGRES_HOST')
                  self.port=os.environ.get('POSTGRES_PORT')
                  self.db=os.environ.get('POSTGRES_DEV_DB')

         def DB_Engine(self):
                  return create_engine(f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}",echo=False)
         
class APIServer():
       def __init__(self):
                self.key = os.environ.get('JWT_PUBLIC_KEY')
                self.algorithms=[os.environ.get('JWT_ALGORITHM')]
                self.port=os.environ.get('PORT')


       def check_authority(self,request: Request):
              token = request.headers.get("Authorization", None)
              print(token)
              if not token:
                     raise HTTPException(401, "Token is missing")  # Raise an error for missing token
              try:
                     payload = decode(token,key = self.key, algorithms=self.algorithms)
              except ExpiredSignatureError as error:
                     raise HTTPException(403, f"Token is invalid: {error}")  # Raise an error for invalid token

