import sqlite3
import json

import pytest

import get_posts
import states


@pytest.fixture
def test_post_output():
    import tests.test_data.test_post_output as output
    return output

@pytest.fixture
def mock_states(monkeypatch):
    # mock the states.py moduel so that the states.get_key returns a None (as a
    # dummy object) and states.set_key does nothing
    monkeypatch.setattr(states, 'get_key', lambda x: None)
    monkeypatch.setattr(states, 'set_key', lambda x,y: None)

@pytest.fixture
def mock_reddit(praw_post_obj):
    # mock the praw.Reddit object
    class MockReddit:
        def __init__(self):
            self.called = False

        def subreddit(self, *args):
            return self

        def new(self, *args, **kwargs):
            if not self.called:
                self.called = True
                return [praw_post_obj]
            else:
                return []

    return MockReddit()

def test_get_post(mock_reddit, mock_states, test_post_output, tmpdir):
    file_name = tmpdir + "/test_db.sqlite"
    reddit = mock_reddit

    get_posts.get_posts(reddit, file_name)

    with sqlite3.connect(file_name) as db:
        cursor = db.cursor()
        posts = cursor.execute('SELECT * FROM posts;').fetchall()
        comments = cursor.execute('SELECT * FROM comments;').fetchall()

    comments_dif = set(comments) ^ set(test_post_output.COMMENTS)
    posts_dif = set(posts) ^ set(test_post_output.POSTS)

    assert not comments_dif
    assert not posts_dif
