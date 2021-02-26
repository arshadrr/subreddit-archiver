import praw

import states
import config
import serializer
import db


def get_post_batch(reddit, subreddit, last_post):
    posts = reddit.subreddit(subreddit).new(
            limit=config.BATCH_SIZE,
            params={'after': last_post}
            )

    return list(posts)

def get_posts(reddit, out_file):
    #TODO: work without credentials
    try:
        last_post = states.get_last_post()
    except KeyError:
        last_post = None
    subreddit = states.get_subreddit()
    db_connection = db.get_connection(out_file)

    posts = get_post_batch(reddit, subreddit, last_post)

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
        states.set_last_post(last_post)

        posts = get_post_batch(reddit, subreddit, last_post)
