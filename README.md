# subreddit-archiver

This utility allows you to save subreddits as SQLite databases. Partial and
complete archives can then be updates with newer posts submitted since the
archival. Allows you to have your personal copy of a subreddit for safekeeping,
analysis, etc.

This tool makes uses of [pushshift.io](https://pushshift.io/), a volunteer-run
service. If you found this tool useful, you can [donate to pushshift.io](https://pushshift.io/donations/) 
as it makes this tool possible.

## Installation

Clone this repository
```
$ git clone https://github.com/arshadrr/subreddit-archiver
```
`cd` into the directory
```
$ cd subreddit-archiver
```
Install the package. Requires Python 3.7 or newer. It's recommended you install
using [pipx](https://pipxproject.github.io/pipx/installation/) (however it does
work with pip).
```
$ pipx install .
```

## Usage

Once installed, the utility can be invoked as `subreddit-archiver` in
your terminal. The utility comes with two commands, `subreddit-archiver archive`
which archives (saves posts from the present to the past, all the way up to the
oldest post in the subreddit if allowed to run long enough) and
`subreddit-archiver update` which saves posts newer than the most recent post in
an archive.

The utility makes use of the Reddit API and takes API credentials through a
configuration file the path to which you pass as an argument (`--credentials`). Instructions on
how to acquire these, and the format the configuration file should take is
described in the section [Credentials](#credentials)

The output of this utility is a SQLite database. For information on the
structure and how to make use of what this program produces, see
[Schema](#schema).

```
$ subreddit-archiver
usage: subreddit-archiver [-h] [--version] {archive,update} ...
```

### `subreddit-archiver archive`
```
$ subreddit-archiver archive -h
usage: subreddit-archiver archive [-h] [--batch-size BATCH_SIZE] --subreddit SUBREDDIT --file FILE --credentials CREDENTIALS

Archive a subreddit.

optional arguments:
  -h, --help            show this help message and exit
  --batch-size BATCH_SIZE
                        Number of posts to fetch from from the Reddit API with each request. Defaults to 100.

required arguments:
  --subreddit SUBREDDIT
                        Name of subreddit to save.
  --file FILE           Location and name of file that output SQLite database should take. e.g ~/archives/mysubreddit.sqlite
  --credentials CREDENTIALS
                        File containing credentials to access Reddit API.

Saves posts and comments from a subreddit to a SQLite database. Archival can be
stopped (e.g Ctr-C) while in progress safely and without data loss. To resume
archival, call with the same arguments (point to the same output file and
subreddit). The output file keeps track of the progress of archival.
```

Suppose you'd like to archive the subreddit `/r/learnart` to the file
`learnart.sqlite` with API credentials stored in `credentials.config`:

```
$ subreddit-archiver archive --subreddit learnart --file learnart.sqlite --credentials credentials.config
Subreddit created on Tue Nov  9 05:18:57 2010
Saved 3 posts more. Covered 0.0% of subreddit lifespan
```
Archival can be stopped (e.g using `Ctr-C`). You can then resume by running the
same command and specifying the same subreddit and output file.

### `subreddit-archiver update`
```
$ subreddit-archiver update -h
usage: subreddit-archiver update [-h] [--batch-size BATCH_SIZE] --file FILE --credentials CREDENTIALS

Update an existing archive of a subreddit.

optional arguments:
  -h, --help            show this help message and exit
  --batch-size BATCH_SIZE
                        Number of posts to fetch from from the Reddit API with each request. Defaults to 100.

required arguments:
  --file FILE           Path to existing archive that should be updated.
  --credentials CREDENTIALS
                        File containing credentials to access Reddit API.

Archives created by this utility keep track of the newest post within them. This command saves posts (and comments under these) newer than the newest post in the archive. Changes to older posts and comments will not be
added. Comments made after a post was saved to an archive will not be added.
```

Suppose you used this tool to create an archive of the `/r/learnart` subreddit.
A few days pass and new posts have been submitted which aren't part of your
archive. To fetch posts submitted since the most recent post in your archive, use
this command.

```
$ subreddit-archiver update --file learnart.sqlite --credentials credentials.config
Newest post in archive is from Mon Mar  8 19:34:26 2021
Saved 1 up to Mon Mar  8 19:53:36 2021
Completed updating
```

## Credentials
To use the Reddit API, this application will need to be provided with API
credentials from Reddit. Follow these instructions to get these:

1. Visit https://www.reddit.com/prefs/apps and click on the button `are you a developer?  create an app...` towards the end of the page.
2. Choose the 'script' option in the list of radio buttons. Give the app a
   name and a redirect-url (anything will do, the values you enter don't really
   matter). Create the app.
3. Copy the text that follows the label `secret` and keep hold of it. This is your `client_secret`.
4. Beneath the text 'personal use script', you'll find a random string of
   letters. Copy this too, it is your `client_id`.
5. Create a text file and paste the `client_id` and `client_secret` in the
   format below:

```
[DEFAULT]
client_id=<insert your client id here>
client_secret=<insert your client secret here>
```

This will be your credentials file. When using this utility, pass the location
of this file to the `--credentials` option.

## Schema
You've saved a bunch of posts. Now what? This section describes what the SQLite
database this utility produces looks like so that you can put it to use. It
required you either install the [SQLite command-line shell](https://sqlite.org/cli.html) or have bindings for SQLite in your
programming language such as [sqlite3](https://docs.python.org/3/library/sqlite3.html) for Python.  


The output database will contain three tables, `archive_metadata`, `comments`
and `posts`:
```
$ sqlite3 learnart.sqlite
-- Loading resources from /home/user/.sqliterc
SQLite version 3.30.0 2019-10-04 15:03:17
Enter ".help" for usage hints.
sqlite> .tables
archive_metadata  comments          posts
```

- `archive_metadata`: stores some metadata about the archive. The specific
  information stored can be found listed in the file
  [states.py](./subreddit_archiver/states.py) in the class
  `DB`.
- `posts`: stores the posts with each row representing one post.
  [schema.sql](./subreddit_archiver/schema.sql)
  contains inline comments explaining the columns that make up this table and how to use them
- `comments`: stores comments with each row representing one comment. As with the
  `posts` table, refer to [schema.sql](./subreddit_archiver/schema.sql) for
  more.
