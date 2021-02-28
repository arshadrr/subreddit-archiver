import argparse

def validate_batch_size(string):
    try:
        batch_size = int(string)
    except ValueError:
        raise argparse.ArgumentTypeError("batch size must be an integer")

    if not batch_size > 0:
        raise argparse.ArgumentTypeError("batch size must be larger than 0")

    return batch_size

