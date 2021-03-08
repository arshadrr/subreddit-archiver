import pickle

import pytest

from subreddit_archiver import db

@pytest.fixture
def db_connection(tmpdir):
    file_name = tmpdir + '/test_db.sqlite'
    return db.get_connection(file_name)

@pytest.fixture(scope="session")
def praw_post_obj():
    with open("tests/test_data/test_post.pickle", "rb") as f:
        return pickle.load(f)
