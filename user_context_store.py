import logging

from pickledb import PickleDB

from user_context import UserContext


class UserContextStore:

    def __init__(self, path):
        try:
            self.path = path
            self.active: dict[str, UserContext] = {}
            logging.info(f"Opening UserContextStore @ {path}")
            self.db = PickleDB(path)
        except Exception as e:
            logging.error(e)
            # os.remove(path)
            self.db = PickleDB(path)

    def load_from_disk(self):
        for key in self.db.all():
            try:
                info = self.db.get(key)
                self.active[key] = UserContext(*info)
                logging.info(f"Restored user context for: {key}")
            except Exception as e:
                logging.error(f"Failed to load context for {key}: {e}")

    def get(self, username: str) -> UserContext:
        return self.active.get(username)

    def set(self, username: str, user_context: UserContext):
        self.active[username] = user_context
        self.db.set(username, user_context.to_tuple())
        self.db.save()

    def remove(self, username):
        self.db.remove(username)
        self.db.save()
        del self.active[username]
