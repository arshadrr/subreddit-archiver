CREATE TABLE archive_metadata (
    -- store metadata about the archive and information relevant to the archival
    -- process. see the DB class in states.py for details on what exactly is
    -- stored in this table.
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT
);

CREATE TABLE posts (
    -- stores posts that have been saved. each row is one post.

    -- the id of the post
    id TEXT PRIMARY KEY NOT NULL,

    -- author will be NULL if the post has been removed/deleted or the author
    -- has deleted their account.
    author TEXT, 
    -- title of the post
    title TEXT,
    -- url that the post points to. If this is a cross-post, url will be the
    -- link of the original post. If the post is a link post, this will be the
    -- link. If the post is a self-post, this will be the same as the permalink.
    url TEXT,
    -- permalink to this post
    permalink TEXT,
    -- if this post is a self-post, the text of the self-post. Otherwise, an
    -- empty string.
    selftext TEXT,

    -- the flair that the poster had as of archival
    author_flair_text TEXT,
    -- the flair that the post had as of archival
    link_flair_text TEXT,

    -- when the post was created, as a unix timestamp
    created_utc INT,
    -- when the post was edited, as a unix timestamp. If the post hasn't been
    -- edited, NULL
    edited INT,
    -- the number of upvotes the post has garnered
    ups INT,
    -- the number of downvotes the post has garnered
    downs INT,
    -- the total score (upvotes - downvotes)
    score INT,
    -- the ratio of upvotes to downvotes
    upvote_ratio REAL,
    -- the number of comments made under this post
    num_comments INT,

    -- if the post has been archived
    archived BOOL,
    -- if the post is a self-post
    is_self BOOL,
    -- if the post is OC
    is_original_content BOOL,
    -- if the post is a video
    is_video BOOL,
    -- if the post has been marked NSFW
    over_18 BOOL
);

CREATE TABLE comments (
    -- stores comments that have been saved. each row is one comment. columns
    -- without a comment explaining them have the same meaning as they do in the
    -- posts table above.

    -- the id of the comment
    id TEXT PRIMARY KEY NOT NULL,

    author TEXT,
    author_flair_text TEXT,
    -- the body text of the comment
    body TEXT,
    -- the id of the comment which this comment is a child of. Suppose there is
    -- a comment A and a user replies with comment B. B will have A's id in this
    -- column. NULL if this is a top-level comment (a comment who's parent is
    -- the post itself)
    parent_comment_id TEXT,
    -- the id of the post under which this comment was made
    post_id TEXT,
    -- is this a top-level comment? A top-level comment is a comment who's
    -- parent is the post itself.
    root BOOL,

    created_utc INT,
    edited INT,
    score INT,
    ups INT,
    downs INT,
    -- the ratio of upvotes to downvotes
    controversiality REAL,

    -- if the commentor is the submitter of the post
    is_submitter BOOL,
    -- if the comment has been stickied
    stickied BOOL
);
