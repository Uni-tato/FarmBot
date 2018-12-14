from csv import Dialect, QUOTE_MINIMAL


class FarmbotCSVDialect(Dialect):
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
