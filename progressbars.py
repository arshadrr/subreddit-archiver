import time

ARCHIVAL_PROGRESS_STRING = """Saved {0} posts more. Covered {1}% of subreddit \
lifespan\r"""

class ArchiveProgressbar:
    def __init__(self, subreddit_created_utc, most_recent_post_utc):
        self.subreddit_created_utc = subreddit_created_utc
        self.most_recent_post_utc = most_recent_post_utc
        self.posts_saved = 0

        print(f"Subreddit created on {time.ctime(subreddit_created_utc)}")

    def tick(self, least_recent_saved_post_utc, posts_saved):
        self.posts_saved += posts_saved 
        print(
                ARCHIVAL_PROGRESS_STRING.format(
                    self.posts_saved,
                    self._lifespan_percentage(least_recent_saved_post_utc)
                    ),
                end=""
                )

    def _lifespan_percentage(self, least_recent_saved_post_utc):
        progress = self.most_recent_post_utc - least_recent_saved_post_utc
        lifespan = self.most_recent_post_utc - self.subreddit_created_utc
        percentage = (progress / lifespan) * 100

        return "{0:.1f}".format(percentage)

    def done(self):
        print("\n")
