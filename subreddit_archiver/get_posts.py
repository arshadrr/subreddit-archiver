import praw
import requests

from subreddit_archiver import (
        states,
        serializer,
        db,
        progressbars
        )


def make_pushshift_url(subreddit, batch_size, post_utc, after):
    url = "https://api.pushshift.io/reddit/search/submission/?"
    url += f"subreddit={subreddit}&size={batch_size}"
    url += "&fields=id&sort=desc"

    if post_utc != None:
        if after:
            url += f"&after={int(post_utc)}"
        else:
            url += f"&before={int(post_utc)}"

    return url

def get_post_batch(reddit, subreddit, batch_size, post_utc, after):
    # TODO network errors
    # TODO keeps showing removed and deleted posts
    url = make_pushshift_url(subreddit, batch_size, post_utc, after)
    request = requests.get(url)

    post_ids = [post['id'] for post in request.json()['data']]
    posts = map(reddit.submission, post_ids)

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
        last_post_utc = state.get_least_recent_post_utc()
    except KeyError:
        last_post_utc = None
    subreddit = state.get_subreddit()

    posts = get_post_batch(reddit, subreddit, batch_size, last_post_utc, False)
    # we've just begun archival and these metadata need to be set
    if last_post_utc == None:
        newest_post = posts[0]
        state.set_most_recent_post_utc(newest_post.created_utc)
    progressbar = progressbars.ArchiveProgressbar(
            state.get_subreddit_created_utc(),
            state.get_most_recent_post_utc()
            )

    while posts:
        process_post_batch(posts, db_connection)

        last_post_utc = posts[-1].created_utc
        state.set_least_recent_post_utc(last_post_utc)
        progressbar.tick(last_post_utc, len(posts))

        posts = get_post_batch(reddit, subreddit, batch_size, last_post_utc, False)

    progressbar.done()

def update_posts(reddit, db_connection, batch_size):
    state = states.State(db_connection)
    newest_post_utc = state.get_most_recent_post_utc()
    subreddit = state.get_subreddit()
    progressbar = progressbars.UpdateProgressbar(newest_post_utc)

    posts = get_post_batch(reddit, subreddit, batch_size, newest_post_utc, True)

    while posts:
        process_post_batch(posts, db_connection)

        newest_post_utc = posts[0].created_utc
        state.set_most_recent_post_utc(newest_post_utc)
        progressbar.tick(newest_post_utc, len(posts))

        posts = get_post_batch(reddit, subreddit, batch_size, newest_post_utc, True)

    progressbar.done()
