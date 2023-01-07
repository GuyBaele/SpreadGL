from datetime import datetime as dt
from datetime import timedelta
from pattern_management import *
import time


def convert_text_to_datetime(text):
    if len(text) == 8:
        text = text[:5] + "0" + text[5:7] + "0" + text[-1]
    if len(text) == 9:
        if text[6] == "-":
            text = text[:5] + "0" + text[5:]
        else:
            text = text[:8] + "0" + text[-1]
    if len(text) == 10:
        text += " 12:00:00"
    if len(text) == 7:
        text += "-16 00:00:00"
    if len(text) == 4:
        text += "-07-01 00:00:00"
    return dt.strptime(text, '%Y-%m-%d %H:%M:%S')


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
    datetime = base + timedelta(seconds=(base.replace(year=base.year + 1) - base).total_seconds() * remain)
    res = datetime.replace(microsecond=0)
    return str(res)


def get_time_info_by_datetime(end_name, duration):
    parsed_name_info = match_date.findall(end_name)
    if parsed_name_info:
        end_text = parsed_name_info[-1]
        end_datetime = convert_text_to_datetime(end_text)
        end_time = convert_datetime_to_decimal_year(end_datetime)
        start_time = end_time - duration
    else:
        start_time = 0.0
        end_time = 0.0
    return start_time, end_time


def get_time_info_by_float(end_name, duration):
    parsed_name_info = match_float.findall(end_name)
    if parsed_name_info:
        end_text = parsed_name_info[-1]
        end_time = float(end_text)
        start_time = end_time - duration
    else:
        start_time = 0.0
        end_time = 0.0
    return start_time, end_time
