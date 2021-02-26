import logging
import warnings
import sys

import praw

import cli
import db
import config
import states
import get_posts


def archive(subreddit, out_file):
    # TODO: validate if a subreddit exists
    if states.get_progress() == states.Progress.IDLE:
        states.set_subreddit(subreddit)
        states.set_progress(states.Progress.SAVING_POSTS)

    if states.get_progress() == states.Progress.SAVING_POSTS:
        reddit = praw.Reddit()
        db_connection = db.get_connection(out_file)
        get_posts.get_posts(reddit, db_connection)

        states.set_progress(states.Progress.COMPLETED)

    if states.get_progress() == states.Progress.COMPLETED:
        print("completed archiving")

if __name__ == "__main__":
    logging.basicConfig(filename=config.LOG_FILE, filemode="a", level=logging.INFO)

    args = cli.get_arg_parser().parse_args()

    if args.command == "archive":
        archive(args.subreddit, args.file)
    else:
        print("update command not implemented")
