import praw

import states
import serializer
import db


def get_post_batch(reddit, subreddit, batch_size, post_id, after):
    if after:
        params = {'after': post_id}
    else:
        params = {'before': post_id}

    posts = reddit.subreddit(subreddit).new(
            limit=batch_size,
            params=params
            )

    return list(posts)

def process_post_batch(posts, db_connection):
    # get all the comments for each post
    for post in posts:
        while True:
            try:
                post.comments.replace_more(limit=None)
                break
            except praw.exceptions.APIException:
                time.sleep(1)


    # serialize the posts as serializer.Submission objects
    posts_serialized = map(serializer.Submission, posts)
    # flatten the comment forest
    comments = []
    for post in posts:
        serializer.flatten_commentforest(post.comments, comments)
    # serialize the comments as serializer.Comment objects
    comments_serialized = map(serializer.Comment, comments)

    # insert posts and comments into the database
    db.insert_posts(db_connection, posts_serialized)
    db.insert_comments(db_connection, comments_serialized)

def archive_posts(reddit, db_connection, batch_size):
    state = states.State(db_connection)
    try:
        last_post = state.get_least_recent_post()
    except KeyError:
        last_post = None
    subreddit = state.get_subreddit()

    posts = get_post_batch(reddit, subreddit, batch_size, last_post, True)
    try:
        state.get_most_recent_post()
    except KeyError:
        newest_post = posts[0].name
        state.set_most_recent_post(newest_post)

    while posts:
        process_post_batch(posts, db_connection)
        print(f"Saved {len(posts)} posts")

        last_post = posts[-1].name
        state.set_least_recent_post(last_post)

        posts = get_post_batch(reddit, subreddit, batch_size, last_post, True)

def update_posts(reddit, db_connection, batch_size):
    state = states.State(db_connection)
    newest_post = state.get_most_recent_post()
    subreddit = state.get_subreddit()

    posts = get_post_batch(reddit, subreddit, batch_size, newest_post, False)

    while posts:
        process_post_batch(posts, db_connection)
        print(f"Saved {len(posts)} posts")

        newest_post = posts[0].name
        state.set_most_recent_post(newest_post)

        posts = get_post_batch(reddit, subreddit, batch_size, newest_post, False)
