import json
import logging

from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from user_context import UserContext

Base = declarative_base()


class UserContextModel(Base):
    __tablename__ = 'user_contexts'

    username = Column(String, primary_key=True)
    password = Column(String, nullable=False)
    user_agent = Column(Text)
    device_id = Column(String)
    bearer_token = Column(Text, default="")
    refresh_token = Column(Text, default="")
    fcm_token = Column(Text, default="")
    cookie_jar = Column(Text, default="")

    def to_user_context(self, on_update=None):
        from user_context import UserContext
        return UserContext(
            username=self.username,
            password=self.password,
            user_agent=self.user_agent,
            device_id=self.device_id,
            bearer_token=self.bearer_token,
            refresh_token=self.refresh_token,
            fcm_token=self.fcm_token,
            cookie_jar=self.cookie_jar,
            on_update=on_update
        )

    @classmethod
    def from_user_context(cls, user_context):
        # Serialize the entire cookie jar to JSON

        cookie_jar_data = ""
        if hasattr(user_context, 'session') and user_context.session.cookies:
            try:
                cookies_list = []
                for cookie in user_context.session.cookies:
                    cookie_dict = {
                        'name': cookie.name,
                        'value': cookie.value,
                        'domain': cookie.domain,
                        'path': cookie.path,
                        'secure': cookie.secure,
                        'expires': cookie.expires
                    }
                    cookies_list.append(cookie_dict)

                # Serialize to JSON string
                cookie_jar_data = json.dumps(cookies_list)
            except Exception as e:
                logging.warning(f"Failed to serialize cookie jar: {e}")

        return cls(
            username=user_context.username,
            password=user_context.password,
            user_agent=user_context.user_agent,
            device_id=user_context.device_id,
            bearer_token=user_context.bearer_token,
            refresh_token=user_context.refresh_token,
            fcm_token=user_context.fcm_token,
            cookie_jar=cookie_jar_data
        )


class UserContextStore:

    def __init__(self, db_url: str):
        logging.info(f"Opening UserContextStore @ {db_url}")
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get(self, username: str) -> UserContext | None:
        context_model = self.session.query(UserContextModel).filter_by(username=username).first()
        if context_model:
            return context_model.to_user_context(on_update=self.set)
        else:
            return None

    def set(self, user_context: UserContext):
        existing = self.session.query(UserContextModel).filter_by(username=user_context.username).first()
        if existing:
            self.session.delete(existing)
            self.session.commit()
        # Add new/updated context
        context_model = UserContextModel.from_user_context(user_context)
        self.session.add(context_model)
        self.session.commit()
