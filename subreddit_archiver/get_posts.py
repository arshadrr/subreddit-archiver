import praw
import prawcore
import requests

from subreddit_archiver import states, serializer, db, progressbars


def get_from_pushshift(url):
    request = requests.get(url)
    if request.status_code in range(500, 600):
        print(f"\nUnable to connect to Pushshift.io, it appears to be down. HTTP {request.status_code}. Exiting.")
        exit(1)

    data = request.json()['data']
    return data

def make_pushshift_url(subreddit, batch_size, post_utc, after):
    # the pushshift.io API is documented at https://github.com/pushshift/api
    url = "https://api.pushshift.io/reddit/search/submission/?"
    url += f"subreddit={subreddit}&size={batch_size}"
    url += "&filter=id&order=desc"

    if post_utc != None:
        if after:
            url += f"&since={int(post_utc)}"
        else:
            url += f"&until={int(post_utc)}"

    return url


def get_ids_from_pushshift(subreddit, batch_size, post_utc, after):
    # fetch post ids from pushshift.

    url = make_pushshift_url(subreddit, batch_size, post_utc, after)
    data = get_from_pushshift(url)
    post_ids = [post["id"] for post in data]

    return post_ids

def get_created_utc(post):
    # when post ids are fetched from pushshift, pushshift sometimes returns
    # posts that are no longer on reddit. attempting to access the post's
    # created_utc property raises a 404 error when praw attempts to get this
    # information from reddit.
    # 
    # this function attempts to access the property. if this errors, the
    # created_utc is fetched from pushshift so that post ids for the next batch
    # can be retrieved
    try:
        return post.created_utc
    except prawcore.exceptions.NotFound:
        url = "https://api.pushshift.io/reddit/search/submission/?"
        url += f"ids={post.id}&fields=created_utc"

        data = get_from_pushshift(url)
        created_utc = data[0]['created_utc']
        return created_utc

def get_post_batch(reddit, subreddit, batch_size, post_utc, after):
    """Get a batch of posts from reddit

    Args:
        post_utc: a unix timestamp. what it represents depends on the value of
                  the 'after' parameter
        after: conveys if 'batch_size' posts should be fetched from after
               'post_utc' or before 'post_utc'.

               If True, go into the future, getting posts after post_utc, i.e,
               newer posts. If False, go into the past, getting posts before
               post_utc, i.e, older posts.

               Will be True when updating the database with newer posts, and
               False when inserting older posts into the database.
    """
    # TODO handle possible network errors on reddit's side

    # Each subreddit's 'new' page only allows to go back 1000 posts in the past.
    # To mitigate this, get post ids from pushshift.io and then fetch posts from
    # the reddit API using these post ids.
    post_ids = get_ids_from_pushshift(subreddit, batch_size, post_utc, after)
    posts = map(reddit.submission, post_ids)

    return list(posts)


def process_post_batch(posts, db_connection):
    # shallow copy to not mutate what's passed to this function
    # posts that may or may not exist on reddit (they could have been removed
    # but remain on pusshift)
    unchecked_posts = posts[::]
    # array that will only contain posts that exist.
    posts = []

    # get all the comments for each post
    for post in unchecked_posts:
        while True:
            try:
                post.comments.replace_more(limit=None)
                posts.append(post)
                break
            # some posts that are on pushshift are removed on reddit and 404.
            except prawcore.exceptions.NotFound:
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
        oldest_post_utc = state.get_least_recent_post_utc()
    except KeyError:
        oldest_post_utc = None
    # get the subreddit the database is archiving
    subreddit = state.get_subreddit()

    posts = get_post_batch(reddit, subreddit, batch_size, oldest_post_utc, False)

    # this is the first run of archiving, set these metadata in the database
    if oldest_post_utc == None:
        # set the newest post in the database to be the newest post in the batch
        # of posts just saved. this information is used for updating the archive
        newest_post = posts[0]
        state.set_most_recent_post_utc(newest_post.created_utc)

    progressbar = progressbars.ArchiveProgressbar(
        state.get_subreddit_created_utc(), state.get_most_recent_post_utc()
    )

    while posts:
        process_post_batch(posts, db_connection)

        oldest_post_utc = get_created_utc(posts[-1])
        # set the oldest post in the database to be the oldest from the batch of
        # posts just saved
        state.set_least_recent_post_utc(oldest_post_utc)
        # update the progress bar
        progressbar.tick(oldest_post_utc, len(posts))

        posts = get_post_batch(reddit, subreddit, batch_size, oldest_post_utc, False)

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

        newest_post_utc = get_created_utc(posts[0])
        # set the newest post in the database to be the newest from the batch of
        # posts just saved
        state.set_most_recent_post_utc(newest_post_utc)
        # update the progress bar
        progressbar.tick(newest_post_utc, len(posts))

        posts = get_post_batch(reddit, subreddit, batch_size, newest_post_utc, True)

    progressbar.done()
