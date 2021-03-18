import praw
import prawcore
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

def get_from_pushshift(subreddit, batch_size, post_utc, after):
    url = make_pushshift_url(subreddit, batch_size, post_utc, after)
    request = requests.get(url)

    data = request.json()['data']
    post_ids = [post['id'] for post in data]

    return post_ids

def get_post_batch(reddit, subreddit, batch_size, post_utc, after):
    '''Get a batch of posts from reddit

    Args:
        post_utc: a unix timestamp. what it represents depends on the value of
                  the 'after' parameter
        after: conveys if 'batch_size' posts should be fetched from after
               'post_utc' or before 'post_utc'.

               If True, go into the future, getting posts newer than those in
               the database. If False, go into the past, getting posts older
               than in the database.

               Will be True when updating the database with newer posts, and
               False when inserting older posts into the database
    '''
    # TODO network errors 
    # TODO keeps showing removed and deleted posts
    # Each subreddit's 'new' page only allows to go back 1000 posts in the past.
    # To mitigate this, get post ids from pushshift.io and then fetch posts from
    # the reddit API using these post ids.
    post_ids = get_from_pushshift(subreddit, batch_size, post_utc, after)
    posts = map(reddit.submission, post_ids)

    return list(posts)

def process_post_batch(posts, db_connection):
    # get all the comments for each post
    for post in posts:
        while True:
            try:
                post.comments.replace_more(limit=None)
                break
            # some posts are removed and 404
            except prawcore.exceptions.NotFound:
                posts.remove(post)
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
    # get the oldest post in the database to continue from
    try:
        last_post_utc = state.get_least_recent_post_utc()
    except KeyError:
        last_post_utc = None
    # get the subreddit the database is archiving
    subreddit = state.get_subreddit()

    posts = get_post_batch(reddit, subreddit, batch_size, last_post_utc, False)
    # this is the first run of archiving, set these metadata in the database
    if last_post_utc == None:
        # set the newest post in the database to be the newest post in the batch
        # of posts just saved. this information is used for updating the archive
        newest_post = posts[0]
        state.set_most_recent_post_utc(newest_post.created_utc)
    progressbar = progressbars.ArchiveProgressbar(
            state.get_subreddit_created_utc(),
            state.get_most_recent_post_utc()
            )

    while posts:
        process_post_batch(posts, db_connection)

        last_post_utc = posts[-1].created_utc
        # set the oldest post in the database to be the oldest from the batch of
        # posts just saved
        state.set_least_recent_post_utc(last_post_utc)
        # update the progress bar
        progressbar.tick(last_post_utc, len(posts))

        posts = get_post_batch(reddit, subreddit, batch_size, last_post_utc, False)

    progressbar.done()

def update_posts(reddit, db_connection, batch_size):
    # load required information from the database
    state = states.State(db_connection)
    newest_post_utc = state.get_most_recent_post_utc()
    subreddit = state.get_subreddit()
    progressbar = progressbars.UpdateProgressbar(newest_post_utc)

    posts = get_post_batch(reddit, subreddit, batch_size, newest_post_utc, True)

    while posts:
        process_post_batch(posts, db_connection)

        newest_post_utc = posts[0].created_utc
        # set the newest post in the database to be the newest from the batch of
        # posts just saved
        state.set_most_recent_post_utc(newest_post_utc)
        # update the progress bar
        progressbar.tick(newest_post_utc, len(posts))

        posts = get_post_batch(reddit, subreddit, batch_size, newest_post_utc, True)

    progressbar.done()
