import praw

import states
import serializer
import db


def get_post_batch(reddit, subreddit, last_post, batch_size):
    posts = reddit.subreddit(subreddit).new(
            limit=batch_size,
            params={'after': last_post}
            )

    return list(posts)

def get_posts(reddit, db_connection, batch_size):
    state = states.State(db_connection)
    try:
        last_post = state.get_last_post()
    except KeyError:
        last_post = None
    subreddit = state.get_subreddit()

    posts = get_post_batch(reddit, subreddit, last_post, batch_size)

    while posts:
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

        print(f"Saved {len(posts)} posts, {len(comments)} comments")

        last_post = posts[-1].name
        state.set_last_post(last_post)

        posts = get_post_batch(reddit, subreddit, last_post, batch_size)
