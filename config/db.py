from sqlalchemy import create_engine, MetaData

engine = create_engine("postgresql+psycopg2://postgres:UNDERTALELAOSTIA@localhost:5432/fastysurvey_db")

meta = MetaData()

conn = engine.connect()