import argparse

DESCRIPTION = """Archive and keep up-to-date an archive of a subreddit."""

ARCHIVE_DESCRIPTION = """Saves posts and comments from a subreddit to a sqlite
database. Archival can be stopped (e.g Ctr-C) while in progress safely and
without data loss. To resume archival, call with the same arguments (point to
the same output file and subreddit)."""

UPDATE_DESCRIPTION = """Archives created by this utility keep track of the
newest post within them. This command saves posts (and comments under these)
newer than the newest post in the archive. Changes to older posts and comments
will not be added. Comments made after a post was saved to an archive will not
be added."""

def get_arg_parser():
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    subparser = parser.add_subparsers(
            required=True,
            help="Supported commands. Call <command> -h for help on specific commands.",
            dest="command"
            )

    archive_parser = subparser.add_parser(
            "archive",
            help="Archive a subreddit.",
            description="Archive a subreddit.",
            epilog=ARCHIVE_DESCRIPTION
            ).add_argument_group('required arguments')
    archive_parser.add_argument(
            "--subreddit",
            required=True,
            help="Name of subreddit to save."
            )
    archive_parser.add_argument(
            "--file",
            required=True,
            help="Location and name of file that output sqlite database should take.\
            e.g ~/archives/mysubreddit.sqlite"
            )

    update_parser = subparser.add_parser(
            "update", 
            help="Update an existing archive of a subreddit.",
            description="Update an existing archive of a subreddit.",
            epilog=UPDATE_DESCRIPTION
            ).add_argument_group('required arguments')
    update_parser.add_argument(
            "--file",
            required=True,
            help="Path to existing archive that should be updated."
            )

    return parser
