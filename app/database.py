from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote_plus
from .config import settings
from urllib.parse import quote_plus

#SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip_address/hostname>/<database_name'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{quote_plus(settings.database_password)}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db(): #ORM
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# import time
# import psycopg
# from psycopg.rows import dict_row #fetch as tuples (immutable), change to dictionary

# while True:
#     try:
#         conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='R3t@Xpfx145970', row_factory=dict_row)
#         cursor = conn.cursor()
#         print("database connection successful!")
#         break
#     except Exception as error:
#         print("Error: ", error)
#         time.sleep(2)

# my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
#             {"title": "title of post 2", "content": "content of post 2", "id": 2}]

# def find_post(id):
#     for p in my_posts:
#         if p["id"] == id:
#             return p
        
# def find_index_post(id):
#     for i, p in enumerate(my_posts):
#         if p["id"] == id:
#             return i