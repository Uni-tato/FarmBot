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


def get_amount(args, type=int):
    """Parse an `int` from `args`.

    Only uses the first element and if it fails to parse as an `int`
    (via a call to `int`), then it returns `1`, otherwise the `int`
    made from the first element of `args`."""
    try:
        # int(float()) because int("5.1") doesn't work.
        int(float(args[0]))
    except (ValueError, IndexError) as e:
        return 1
    else:
        if isinstance(type, float):
            return float(args[0])
        else:
            return int(float(args[0]))


def get_name(args, allow_ints=False):
    """Parse a name from `args`.

    It will not include the first element if it is an `int` type, or if it is a "*" character.
    Hence, names which begin in numbers are not allowed."""
    if allow_ints:
        return " ".join(args).strip()

    try:
        int(args[0])
    except ValueError:
        if args[0] is "*":
            return " ".join(args[1:]).strip()
        return " ".join(args).strip()
    else:
        return " ".join(args[1:]).strip()
