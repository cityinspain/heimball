import pandas as pd
from sqlalchemy import create_engine

df = pd.read_csv('data/people_processed.csv')

engine = create_engine(
    'postgresql+psycopg2://postgres:postgres@localhost:5432/postgres')
df.to_sql('register', engine, if_exists='replace', index=False)
