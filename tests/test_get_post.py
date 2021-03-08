import sqlite3
import json

import pytest

from subreddit_archiver import (
        get_posts,
        states
        )


@pytest.fixture
def test_post_output():
    import tests.test_data.test_post_output as output
    return output

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

@pytest.fixture
def setup_states(db_connection):
    state = states.State(db_connection)
    state.set_subreddit('learnart')
    state.set_subreddit_created_utc(0)

def test_archive_post(mock_reddit, setup_states, test_post_output, db_connection):
    reddit = mock_reddit

    get_posts.archive_posts(reddit, db_connection, 100)

    cursor = db_connection.cursor()
    posts = cursor.execute('SELECT * FROM posts ORDER BY id;').fetchall()
    comments = cursor.execute('SELECT * FROM comments ORDER BY id;').fetchall()

    assert comments == test_post_output.COMMENTS
    assert posts == test_post_output.POSTS
