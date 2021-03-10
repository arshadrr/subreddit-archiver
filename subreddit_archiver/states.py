import enum

from subreddit_archiver import db

class DB(enum.Enum):
    """Keys that the table archive_metadata keeps track of"""

    # stores a value of the Progress enum, represents the state of archival
    PROGRESS = "archival_progress"
    # the name of the subreddit being archivedd
    SUBREDDIT = "subreddit"
    # when the subreddit was created, as a unix timestamp
    CREATED_UTC = "subreddit_created_utc"
    # the post id of the newest post in the archive
    MOST_RECENT_POST = "most_recent_saved_post"
    # the post id of the oldest most in the archive
    LEAST_RECENT_POST = "least_recent_saved_post"
    # when the newest post in the archive was created, as a unix timestamp
    MOST_RECENT_POST_UTC = "most_recent_saved_post_utc"

class Progress(enum.Enum):
    """Values the DB.PROGRESS key can take in the db"""

    # conveys that archival has not yet begun
    IDLE = 1
    # conveys that archival has begun and is in progress
    SAVING_POSTS = 2
    # conveys that archival is complete
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
            progress = Progress(int(self.get_key(DB.PROGRESS)))
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

    def get_least_recent_post(self):
        return self.get_key(DB.LEAST_RECENT_POST)

    def set_least_recent_post(self, least_recent_post_id):
        self.set_key(DB.LEAST_RECENT_POST, least_recent_post_id)

    def get_most_recent_post(self):
        return self.get_key(DB.MOST_RECENT_POST)

    def set_most_recent_post(self, most_recent_post_id):
        self.set_key(DB.MOST_RECENT_POST, most_recent_post_id)

    def get_subreddit_created_utc(self):
        return int(float(self.get_key(DB.CREATED_UTC)))

    def set_subreddit_created_utc(self, created_utc):
        self.set_key(DB.CREATED_UTC, created_utc)

    def get_most_recent_post_utc(self):
        return int(float(self.get_key(DB.MOST_RECENT_POST_UTC)))

    def set_most_recent_post_utc(self, most_recent_post_id_utc):
        self.set_key(DB.MOST_RECENT_POST_UTC, most_recent_post_id_utc)
