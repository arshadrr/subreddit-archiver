import enum

import config
import db

class DB(enum.Enum):
    """Keys that the dbm that keeps track of states can take"""

    PROGRESS = "archival_progress"
    SUBREDDIT = "subreddit"
    LAST_POST = "last_saved_post"

class Progress(enum.Enum):
    """Values the DB.PROGRESS key can take in the db"""

    IDLE = 1
    SAVING_POSTS = 2
    COMPLETED = 3


class State:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def set_key(self, key, value):
        """Record a value under a key

        Args:
            key: The key to record the value under. An attribute of DB.
            value: The value to store.
        """

        db.set_kv(self.db_connection, key.value, value)

    def get_key(self, key):
        """Get a key from the database

        Args:
            key: The key under which the required value is stored. An attribute of DB.

        Returns:
            The string stored under the key.
        """

        return db.get_kv(self.db_connection, key.value)

    def get_progress(self):
        try:
            progress = Progress(self.get_key(DB.PROGRESS))
        except KeyError:
            progress = Progress.IDLE
            self.set_key(DB.PROGRESS, Progress.IDLE.value)

        return progress

    def set_progress(self, progress):
        self.set_key(DB.PROGRESS, progress.value)

    def get_subreddit(self):
        return self.get_key(DB.SUBREDDIT)

    def set_subreddit(self, subreddit):
        self.set_key(DB.SUBREDDIT, subreddit)

    def get_last_post(self):
        return self.get_key(DB.LAST_POST)

    def set_last_post(self, last_post_id):
        self.set_key(DB.LAST_POST, last_post_id)
