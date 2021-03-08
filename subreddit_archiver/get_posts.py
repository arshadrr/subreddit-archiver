import praw

from subreddit_archiver import (
        states,
        serializer,
        db,
        progressbars
        )


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
        last_post_id = state.get_least_recent_post()
    except KeyError:
        last_post_id = None
    subreddit = state.get_subreddit()

    posts = get_post_batch(reddit, subreddit, batch_size, last_post_id, True)
    # we've just begun archival and these metadata need to be set
    if last_post_id == None:
        newest_post = posts[0]
        state.set_most_recent_post(newest_post.name)
        state.set_most_recent_post_utc(newest_post.created_utc)
    progressbar = progressbars.ArchiveProgressbar(
            state.get_subreddit_created_utc(),
            state.get_most_recent_post_utc()
            )

    while posts:
        process_post_batch(posts, db_connection)

        last_post = posts[-1]
        state.set_least_recent_post(last_post.name)
        progressbar.tick(last_post.created_utc, len(posts))

        posts = get_post_batch(reddit, subreddit, batch_size, last_post.name, True)

    progressbar.done()

def update_posts(reddit, db_connection, batch_size):
    state = states.State(db_connection)
    newest_post_id = state.get_most_recent_post()
    subreddit = state.get_subreddit()
    progressbar = progressbars.UpdateProgressbar(state.get_most_recent_post_utc())

    posts = get_post_batch(reddit, subreddit, batch_size, newest_post_id, False)

    while posts:
        process_post_batch(posts, db_connection)

        newest_post = posts[0]
        state.set_most_recent_post(newest_post.name)
        state.set_most_recent_post_utc(newest_post.created_utc)
        progressbar.tick(newest_post.created_utc, len(posts))

        posts = get_post_batch(reddit, subreddit, batch_size, newest_post.name, False)

    progressbar.done()
