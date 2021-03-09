# subreddit-archiver

This utility allows you to save subreddits as SQLite databases. Partial and
complete archives can then be updates with newer posts submitted since the
archival. Allows you to have your personal copy of a subreddit for safekeeping,
analysis, etc.

## Installation

Clone this repository
```
$ git clone https://github.com/arshadrr/subreddit-archiver
```
`cd` into the directory
```
$ cd subreddit-archiver
```
Install the package
```
$ pip install .
```

## Usage

Once installed, the utlity can be invoked as `subreddit-archiver` in
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
structure and how to make use of what this programn produces, see
[Schema](#schema).

```
$ subreddit-archiver
usage: subreddit-archiver [-h] {archive,update} ...
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
  --file FILE           Location and name of file that output sqlite database should take. e.g ~/archives/mysubreddit.sqlite
  --credentials CREDENTIALS
                        File containing credentials to access Reddit API.

Saves posts and comments from a subreddit to a sqlite database. Archival can be
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
archive. To fetch posts submitted since the most recent post in your arcive, use
this command.

```
$ subreddit-archiver update --file learnart.sqlite --credentials credentials.config
Newest post in archive is from Mon Mar  8 19:34:26 2021
Saved 1 up to Mon Mar  8 19:53:36 2021
Completed updating
```

## Credentials

## Schema
