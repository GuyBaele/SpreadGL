from datetime import datetime as dt
from datetime import timedelta as td


def convert_decimal_year_to_datetime(decimal):
    year = int(decimal)
    remain = decimal - year
    base = dt(year, 1, 1)
    datetime = base + td(seconds=(base.replace(year=base.year + 1) - base).total_seconds() * remain)
    res = datetime.replace(microsecond=0)
    return str(res)
