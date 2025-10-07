from typing import List, Set

from sqlalchemy import Column, String, Text, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

Base = declarative_base()


class SchedulerContextModel(Base):
    __tablename__ = 'apscheduler_context'
    id = Column(String, primary_key=True)
    last_seen = Column(Text, nullable=False)  # comma-separated list of strings

    def get_last_seen_list(self) -> List[str]:
        return [x for x in self.last_seen.split(',') if x]

    def set_last_seen_list(self, values: List[str]):
        self.last_seen = ','.join(values)


class SchedulerContextStore:
    def __init__(self, engine: Engine, session: sessionmaker[Session]):
        self.engine = engine
        self.session = session
        Base.metadata.create_all(self.engine)

    def get(self, id: str) -> Set[str]:
        session = self.session()
        try:
            row = session.query(SchedulerContextModel).filter_by(id=id).first()
            if row:
                return set(row.get_last_seen_list())
            return set()
        finally:
            session.close()

    def put(self, id: str, values: List[str]):
        session = self.session()
        try:
            row = session.query(SchedulerContextModel).filter_by(id=id).first()
            if row:
                row.set_last_seen_list(values)
            else:
                row = SchedulerContextModel(id=id, last_seen=','.join(values))
                session.add(row)
            session.commit()
        finally:
            session.close()

    def remove(self, id: str):
        session = self.session()
        try:
            row = session.query(SchedulerContextModel).filter_by(id=id).first()
            if row:
                session.delete(row)
                session.commit()
        finally:
            session.close()
