import logging
import warnings
import sys

import praw

import cli
import db
import config
import states
import get_posts


def archive(subreddit, out_file, batch_size):
    # TODO: validate if a subreddit exists
    db_connection = db.get_connection(out_file)
    state = states.State(db_connection)

    if state.get_progress() == state.Progress.IDLE:
        state.set_subreddit(subreddit)
        state.set_progress(state.Progress.SAVING_POSTS)

    if state.get_progress() == state.Progress.SAVING_POSTS:
        reddit = praw.Reddit()
        get_posts.get_posts(reddit, db_connection, batch_size)

        state.set_progress(state.Progress.COMPLETED)

    if state.get_progress() == state.Progress.COMPLETED:
        print("completed archiving")

if __name__ == "__main__":
    logging.basicConfig(filename=config.LOG_FILE, filemode="a", level=logging.INFO)

    args = cli.get_arg_parser().parse_args()

    if args.command == "archive":
        archive(args.subreddit, args.file, args.batch_size)
    else:
        print("update command not implemented")
