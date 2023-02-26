from datetime import datetime as dt
from datetime import timedelta as td
import time


def convert_datetext_to_datetime(text):
    year = None
    month = None
    day = None
    # Split text by '-'
    parts = text.split("-")
    # Extract year, month and day values
    if len(parts) >= 1:
        year = int(parts[0])
    if len(parts) >= 2:
        month = int(parts[1])
    if len(parts) == 3:
        day = int(parts[2])
    # If month or day is missing, assume middle of that month or day
    if month is None:
        month = 7
    if day is None:
        days_in_month = 31
        if month in [4, 6, 9, 11]:
            days_in_month = 30
        elif month == 2:
            if year is None or (year % 4 != 0 or (year % 100 == 0 and year % 400 != 0)):
                days_in_month = 28
            else:
                days_in_month = 29
        day = (days_in_month + 1) // 2
    # Convert to datetime object
    dt_obj = dt(year=year, month=month, day=day, hour=12, minute=0, second=0)
    return dt_obj


def time_stamp_since_unix_epoch(datetime):
    return time.mktime(datetime.timetuple())


def convert_datetime_to_decimal_year(datetime):
    year = datetime.year
    start_of_this_year = dt(year=year, month=1, day=1)
    start_of_next_year = dt(year=year + 1, month=1, day=1)
    year_elapsed = time_stamp_since_unix_epoch(datetime) - time_stamp_since_unix_epoch(start_of_this_year)
    year_duration = time_stamp_since_unix_epoch(start_of_next_year) - time_stamp_since_unix_epoch(start_of_this_year)
    fraction = year_elapsed / year_duration
    return year + fraction


def convert_decimal_year_to_datetime(decimal):
    year = int(decimal)
    remain = decimal - year
    base = dt(year, 1, 1)
    datetime = base + td(seconds=(base.replace(year=base.year + 1) - base).total_seconds() * remain)
    res = datetime.replace(microsecond=0)
    return str(res)


def convert_datetime_to_timestamp(datetime):
    return dt.timestamp(dt.strptime(datetime, '%Y-%m-%d %H:%M:%S'))
