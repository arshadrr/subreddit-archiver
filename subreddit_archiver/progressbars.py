import time

ARCHIVAL_PROGRESS_STRING = """Saved {0} posts more. Covered {1}% of subreddit \
lifespan\r"""
UPDATE_PROGRESS_STRING = """Saved {0} up to {1}\r"""

class ArchiveProgressbar:
    def __init__(self, subreddit_created_utc, most_recent_post_utc):
        self.subreddit_created_utc = subreddit_created_utc
        self.most_recent_post_utc = most_recent_post_utc
        self.posts_saved = 0

        print(f"Subreddit created on {time.ctime(subreddit_created_utc)}")
        print("Preparing to archive or continue archival", end="\r")

    def tick(self, least_recent_saved_post_utc, posts_saved):
        self.posts_saved += posts_saved 
        print(
                ARCHIVAL_PROGRESS_STRING.format(
                    self.posts_saved,
                    self._lifespan_percentage(least_recent_saved_post_utc)
                    ),
                end="\r"
                )

    def _lifespan_percentage(self, least_recent_saved_post_utc):
        progress = self.most_recent_post_utc - least_recent_saved_post_utc
        lifespan = self.most_recent_post_utc - self.subreddit_created_utc
        percentage = (progress / lifespan) * 100

        return "{0:.1f}".format(percentage)

    def done(self):
        # The oldest post in the subreddit couldn't have been created at the
        # same time as the subreddit was, so the progressbar won't reach 100%.
        # To convey completion, tick one last time, pretendinding a post created
        # at subreddit creation time was saved to get it to 100%
        self.tick(self.subreddit_created_utc, 0)
        print("\n")

class UpdateProgressbar:
    def __init__(self, most_recent_post_utc):
        self.posts_saved = 0
        print(f"Newest post in archive is from {time.ctime(most_recent_post_utc)}")
        print("Preparing to update the archive", end="\r")

    def tick(self, most_recent_post_utc, posts_saved):
        self.posts_saved += posts_saved
        print(
                UPDATE_PROGRESS_STRING.format(
                    self.posts_saved,
                    time.ctime(most_recent_post_utc)
                    ),
                end="\r"
                )

    def done(self):
        print("\nCompleted updating")
