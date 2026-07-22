from datetime import datetime as dt
from datetime import timedelta as td
import time


def convert_datetext_to_datetime(text, format='YYYY-MM-DD'):
    year = None
    month = None
    day = None
    # Split text by '-'
    parts = text.split("-")

    # Extract year, month and day values based on the specified format
    if format == 'YYYY-MM-DD':
        if len(parts) >= 1:
            year = int(parts[0])
        if len(parts) >= 2:
            month = int(parts[1])
        if len(parts) == 3:
            day = int(parts[2])
    elif format == 'DD-MM-YYYY':
        if len(parts) >= 1:
            day = int(parts[0])
        if len(parts) >= 2:
            month = int(parts[1])
        if len(parts) == 3:
            year = int(parts[2])
    else:
        raise ValueError("Unsupported date format!")
    
    # If month or day is missing, assume first of that month or day
    if month is None:
        month = 1
    if day is None:
        day = 1
        
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
