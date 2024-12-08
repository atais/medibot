import logging
import os
import pickle
import uuid

import appdirs
import attr
from fake_useragent import UserAgent

_cache_dir = appdirs.user_cache_dir("medibot")


@attr.s
class UserData:
    username: str = attr.ib()
    user_agent: str = attr.ib(default=UserAgent().random)
    device_id: str = attr.ib(default=str(uuid.uuid4()))
    bearer_token: str = attr.ib(default="")
    refresh_token: str = attr.ib(default="")

    def __attrs_post_init__(self):
        self.cache = _cache_dir + "/" + self.username
        try:
            with open(self.cache, 'rb') as f:
                profile = pickle.load(f)
                self.__dict__.update(profile.__dict__)
            logging.debug(f"Restored profile for {self.username}, {self}")
        except FileNotFoundError:
            logging.debug(f"Created new profile for {self.username}, {self}")

    def update_tokens(self, bearer: str, refresh: str) -> None:
        self.bearer_token = bearer
        self.refresh_token = refresh
        os.makedirs(os.path.dirname(self.cache), exist_ok=True)
        with open(self.cache, 'wb') as f:
            pickle.dump(self, f)
            logging.debug(f"Saved profile for {self.username}")
