import argparse
import os
import collections
import configparser

Credentials = collections.namedtuple(
        "Credentials",
        ['client_id', 'client_secret']
        )

def validate_batch_size(string):
    try:
        batch_size = int(string)
    except ValueError:
        raise argparse.ArgumentTypeError("batch size must be an integer")

    if not batch_size > 0:
        raise argparse.ArgumentTypeError("batch size must be larger than 0")

    return batch_size

def validate_credentials_file(string):
    if not os.path.exists(string):
        raise argparse.ArgumentTypeError("credentials file does not exist")

    config = configparser.ConfigParser()
    config.read(string)
    
    try:
        config["DEFAULT"]
    except KeyError:
        raise argparse.ArgumentTypeError("invalid format of credentials file")

    try:
        client_id = config["DEFAULT"]["client_id"]
    except KeyError:
        raise argparse.ArgumentTypeError("credentials file doesn't include\
        client_id")

    try:
        client_secret = config["DEFAULT"]["client_secret"]
    except KeyError:
        raise argparse.ArgumentTypeError("credentials file doesn't include\
        client_secret")

    return Credentials(client_id, client_secret)
