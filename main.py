import logging
import warnings
import sys

import config
import states
import get_posts

if __name__ == "__main__":
    logging.basicConfig(filename=config.LOG_FILE, filemode="a", level=logging.INFO)

    if states.get_progress() == states.Progress.IDLE:
        try:
            #TODO check if a subreddit exists
            subreddit = sys.argv[1]
        except IndexError:
            warnings.warn("Provide name of subreddit to archive")
            exit()

        states.set_subreddit(subreddit)
        states.set_progress(states.Progress.SAVING_POSTS)

    if states.get_progress() == states.Progress.SAVING_POSTS:
        get_posts.get_posts()

        states.set_subreddit(None)
        states.set_progress(states.Progress.IDLE)
        states.set_last_post(None)
