from sqlalchemy import inspect
from sqlalchemy.engine import Inspector
from sqlmodel import Session, create_engine

import settings

POSTGRES_URL = settings.POSTGRES_URL

engine = create_engine(POSTGRES_URL, echo=settings.DEBUG)


def get_session():
    with Session(engine) as session:
        yield session


def get_inspector() -> Inspector:
    return inspect(engine)
