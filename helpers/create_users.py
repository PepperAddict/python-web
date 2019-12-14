import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey, UniqueConstraint
from sqlalchemy import inspect

metadata = MetaData()

books = Table('users', metadata,
              Column('id', Integer, primary_key=True),
              Column('name', String),
              Column('username', String),
              Column('password', String),
              UniqueConstraint('username')
              )

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)