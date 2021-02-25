import dbm
import enum

import config

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

def set_key(key, value):
    """Record a value under a key

    Args:
        key: The key to record the value under. An attribute of DB.
        value: The value to store.
    """

    with dbm.open(config.STATES_FILE, "c") as db:
        if value == None:
            del db[key.value]
        else:
            db[key.value] = str(value)

def get_key(key):
    """Get a key from the dbm

    Args:
        key: The key under which the required value is stored. An attribute of DB.

    Returns:
        The string stored under the key.
    """

    with dbm.open(config.STATES_FILE, "c") as db:
        return db[key.value].decode()

def get_progress():
    try:
        progress = Progress(int(get_key(DB.PROGRESS)))
    except KeyError:
        progress = Progress.IDLE
        set_key(DB.PROGRESS, Progress.IDLE.value)

    return progress

def set_progress(progress):
    set_key(DB.PROGRESS, progress.value)

def get_subreddit():
    return get_key(DB.SUBREDDIT)

def set_subreddit(subreddit):
    set_key(DB.SUBREDDIT, subreddit)

def get_last_post():
    return get_key(DB.LAST_POST)

def set_last_post(last_post_id):
    set_key(DB.LAST_POST, last_post_id)
