"""Provide various utilities for use throughout the bot."""
from csv import Dialect, QUOTE_MINIMAL


class FarmbotCSVDialect(Dialect):
    """Specifies what the CSV files in the project should parse as.

    Because CSV is not a standardised format, mutually incompatible
    dialects of CSV exist. This extends to our dialect."""
    delimiter = ","
    quotechar = '"'
    doublequote = True
    skipinitialspace = True
    lineterminator = "\r\n"
    quoting = QUOTE_MINIMAL


def get_amount(args):
    try:
        int(args[0])
    except ValueError:
        return 1
    else:
        return int(args[0])


def get_name(args, allow_ints=False):
    if allow_ints:
        return " ".join(args).strip()

    try:
        int(args[0])
    except ValueError:
        return " ".join(args).strip()
    else:
        return " ".join(args[1:]).strip()
