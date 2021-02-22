import os

import pytest

import config
import states


def test_hi(tmpdir, monkeypatch):
    monkeypatch.setattr(
            config,
            'STATES_FILE',
            os.path.join(tmpdir, config.STATES_FILE)
            )


    states.set_key(states.DB.SUBREDDIT, 'hello')
    assert states.get_key(states.DB.SUBREDDIT) == 'hello'
