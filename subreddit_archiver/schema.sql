CREATE TABLE archive_metadata (
    key TEXT PRIMARY KEY NOT NULL,
    value TEXT
);

CREATE TABLE posts (
    id TEXT PRIMARY KEY NOT NULL,

    -- author will be NULL if the post has been removed/deleted or the author
    -- has deleted their account.
    author TEXT, 
    title TEXT,
    url TEXT,
    permalink TEXT,
    selftext TEXT,

    author_flair_text TEXT,
    link_flair_text TEXT,

    created_utc INT,
    -- edited is NULL if the post hasn't been edited. Otherwise unix time of
    -- when it was edited
    edited INT,
    ups INT,
    downs INT,
    score INT,
    upvote_ratio REAL,
    num_comments INT,

    archived BOOL,
    is_self BOOL,
    is_original_content BOOL,
    is_video BOOL,
    over_18 BOOL
);

CREATE TABLE comments (
    id TEXT PRIMARY KEY NOT NULL,

    author TEXT,
    author_flair_text TEXT,
    body TEXT,
    -- NULL if this is it's a top-level comment
    parent_comment_id TEXT,
    post_id TEXT,
    -- is this a top-level comment?
    root BOOL,

    created_utc INT,
    -- edited is NULL if the comment hasn't been edited. Otherwise unix time of
    -- when it was edited
    edited INT,
    score INT,
    ups INT,
    downs INT,
    controversiality REAL,

    is_submitter BOOL,
    stickied BOOL
);
