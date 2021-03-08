import os

import pytest

from subreddit_archiver import states


def test_states(db_connection):
    state = states.State(db_connection)

    state.set_key(states.DB.SUBREDDIT, 'hello')
    assert state.get_key(states.DB.SUBREDDIT) == 'hello'
