from csv import Dialect, QUOTE_MINIMAL


class FarmbotCSVDialect(Dialect):
    delimiter = ","
    quotechar = '"'
    doublequote = True
    skipinitialspace = True
    lineterminator = "\r\n"
    quoting = QUOTE_MINIMAL
