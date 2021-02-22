import praw


SUBMISSION_FIELDS = {
        "fields": [
            "id",
            "author",
            "title",
            "url",
            "permalink",
            "selftext",
            "author_flair_text",
            "link_flair_text",
            "created_utc",
            "edited",
            "ups",
            "downs",
            "score",
            "upvote_ratio",
            "num_comments",
            "archived",
            "is_self",
            "is_original_content",
            "is_video",
            "over_18"
            ],
        # the values of some fields must be assigned manually and shouldn't take
        # the value the attribute has on the praw.models.Submission object
        # provided
        "post-process": [
            "author",
            "edited"
            ]
        }

COMMENT_FIELDS = {
        "fields": [
            "id",
            "author",
            "author_flair_text",
            "body",
            "parent_id",
            "submission_id",
            "is_root",
            "created_utc",
            "edited",
            "score",
            "ups",
            "downs",
            "controversiality",
            "is_submitter",
            "stickied"
            ],
        # the values of some fields must be assigned manually and shouldn't take
        # the value the attribute has on the praw.models.Comment object
        # provided
        "post-process": [
            "author",
            "parent_id",
            "submission_id",
            "edited"
            ]
        }

class FromFieldList:
    """Extract fields listed in the fields dictionary from a source object,
    assigning the values to self. Implements the sequence protocol so that it
    can be passed to sqlite3.executemany

    Args:
        fields: a dictionary with two lists: one under the key "fields" that
        lists all fields that will exist and another under the key
        "post-process" that will be assigned manually later.
    """
    def __init__(self, fields, source):
        # extract the allowed fields from the source object and assign them to
        # self. fields in "post-process" need to be processed manually.
        for field in fields["fields"]:
            if not field in fields["post-process"]:
                setattr(self, field, getattr(source, field))

        self.fields = fields["fields"]

    def __iter__(self):
        for field in self.fields:
            yield getattr(self, field)

    def __getitem__(self, index):
        return getattr(self, self.fields[index])

    def __len__(self):
        return len(self.fields)

class Submission(FromFieldList):
    """Extracts fields from a praw.models.Submission object that are listed in
    SUBMISSION_FIELDS. These are the fields that will be saved in the
    posts table in the output sqlite database.

    Args:
        submission: a praw.models.Submission object
    """
    def __init__(self, submission):
        # extract fields that don't need to manually be extracted
        super().__init__(SUBMISSION_FIELDS, submission)

        # manually assign to self the fields that FromFieldList's __init__ should not
        # have retrieved from the praw.models.Submission, the submission object
        if submission.author:
            self.author = submission.author.name
        else:
            self.author = None

        # False gets stored as 0 in sqlite. None gets stored as NULL and makes
        # more sense to indicate that the item has not been edited
        if submission.edited == False:
            self.edited = None
        else:
            self.edited = submission.edited

class Comment(FromFieldList):
    """Extracts fields from a praw.models.Comment object that are listed in
    COMMENT_FIELDS. These are the fields that will be saved in the comments
    table in the output sqlite database.

    Args:
        comment: a praw.models.Comment object
    """
    def __init__(self, comment):
        # extract fields that don't need to manually be extracted
        super().__init__(COMMENT_FIELDS, comment)

        # manually assign to self the fields that FromFieldList's __init__ should not
        # have retrieved from the praw.models.Comment, the comment object
        if comment.author:
            self.author = comment.author.name
        else:
            self.author = None

        self.submission_id = comment.submission.id

        if not self.is_root:
            self.parent_id = comment.parent().id
        else:
            self.parent_id = None

        # False gets stored as 0 in sqlite. None gets stored as NULL and makes
        # more sense to indicate that the item has not been edited
        if comment.edited == False:
            self.edited = None
        else:
            self.edited = comment.edited

def flatten_commentforest(commentforest, outlist):
    """Flatten a praw.models.comment_forest.CommentForest object

    Args:
        commentforest: an instance of praw.models.comment_forest.CommentForest
        outlist: a list to append the comments in
    """

    for comment in commentforest:
        outlist.append(comment)
        flatten_commentforest(comment.replies, outlist)
