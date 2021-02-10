import unittest
import tempfile
import os
import shutil

import config
import states
import serializer

import praw


class TestStates(unittest.TestCase):
    def setUp(self):
        tempdir = tempfile.mkdtemp()
        config.STATES_FILE = os.path.join(tempdir, config.STATES_FILE)

    def tearDown(self):
        shutil.rmtree(os.path.split(config.STATES_FILE)[0])

    def test_get_set_key(self):
        states.set_key(states.DB.SUBREDDIT, 'hello')
        self.assertEqual(
                states.get_key(states.DB.SUBREDDIT),
                'hello'
                )

class TestSerializers:
    pass

if __name__ == "__main__":
    unittest.main()
