import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, UniqueConstraint
from sqlalchemy import inspect

metadata = MetaData()

books = Table('reviews', metadata,
              Column('id', Integer, primary_key=True),
              Column('isbn', String),
              Column('username', String),
              Column('rating', String),
              Column('review', String)
              )

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)