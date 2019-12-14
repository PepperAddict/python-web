import csv
import os
import python-dotenv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy import inspect

metadata = MetaData()

books = Table('books', metadata,
              Column('id', Integer, primary_key=True),
              Column('isbn', String),
              Column('title', String),
              Column('author', String),
              Column('year', Integer),
              )

engine = create_engine(os.getenv("DATABASE_URL"))
metadata.create_all(engine)
