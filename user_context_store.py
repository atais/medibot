from typing import List

from sqlalchemy import Column, String, Text, Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

from user_context import CookieInfo, UserContext, UserData

Base = declarative_base()


class UserContextModel(Base):
    __tablename__ = 'user_contexts'

    username = Column(String, primary_key=True)
    data = Column(Text, nullable=False)

    def to_user_context(self, on_update=None):
        return UserContext(
            data=UserData.model_validate_json(self.data),
            on_update=on_update
        )

    @classmethod
    def from_user_context(cls, user_context):
        user_context.data.cookie_jar = []
        for cookie in user_context.session.cookies:
            cookie = CookieInfo(
                name=cookie.name,
                value=cookie.value,
                domain=cookie.domain,
                path=cookie.path,
                secure=cookie.secure,
                expires=cookie.expires
            )
            user_context.data.cookie_jar.append(cookie)

        return cls(
            username=user_context.data.username,
            data=user_context.data.model_dump_json()
        )


class UserContextStore:
    def __init__(self, engine: Engine, session: sessionmaker[Session]):
        self.engine = engine
        self.session = session
        Base.metadata.create_all(self.engine)

    def get_all(self) -> List[UserData]:
        session = self.session()
        try:
            context_models = session.query(UserContextModel).all()
            ucs = [model.to_user_context(on_update=lambda ctx: ctx) for model in context_models]
            return [u.data for u in ucs]
        finally:
            session.close()

    def get(self, username: str) -> UserContext | None:
        session = self.session()
        try:
            context_model = session.query(UserContextModel).filter_by(username=username).first()
            if context_model:
                return context_model.to_user_context(on_update=self.set)
            else:
                return None
        finally:
            session.close()

    def set(self, user_context: UserContext):
        session = self.session()
        try:
            existing = session.query(UserContextModel).filter_by(username=user_context.data.username).first()
            if existing:
                session.delete(existing)
                session.commit()
            context_model = UserContextModel.from_user_context(user_context)
            session.add(context_model)
            session.commit()
        finally:
            session.close()
