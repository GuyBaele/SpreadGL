from datetime import datetime as dt
from datetime import timedelta
from PatternManagement import *
import time


def textToDateTime(date):
    if len(date) == 8:
        date = date[:5] + "0" + date[5:7] + "0" + date[-1]
    if len(date) == 9:
        if date[6] == "-":
            date = date[:5] + "0" + date[5:]
        else:
            date = date[:8] + "0" + date[-1]
    if len(date) == 10:
        date += " 12:00:00"
    if len(date) == 7:
        date += "-16 00:00:00"
    if len(date) == 4:
        date += "-07-01 00:00:00"
    return dt.strptime(date, '%Y-%m-%d %H:%M:%S')


def timeStampSinceEpoch(date):
    return time.mktime(date.timetuple())


def dateTimeToDecimal(date):
    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year + 1, month=1, day=1)
    yearElapsed = timeStampSinceEpoch(date) - timeStampSinceEpoch(startOfThisYear)
    yearDuration = timeStampSinceEpoch(startOfNextYear) - timeStampSinceEpoch(startOfThisYear)
    fraction = yearElapsed / yearDuration
    return date.year + fraction


def decimalToDateTime(decimal):
    year = int(decimal)
    rem = decimal - year
    base = dt(year, 1, 1)
    datetime = base + timedelta(seconds=(base.replace(year=base.year + 1) - base).total_seconds() * rem)
    res = datetime.replace(microsecond=0)
    return str(res)


def dateToEndTime(end_name, duration):
    parsed_name_info = matchDate.findall(end_name)
    if parsed_name_info:
        endDate = parsed_name_info[-1]
        endDateTime = textToDateTime(endDate)
        end_time = dateTimeToDecimal(endDateTime)
        start_time = end_time - duration
    else:
        start_time = 0.0
        end_time = 0.0
    return end_time, start_time


def floatToEndTime(end_name, duration):
    parsed_name_info = matchFloat.findall(end_name)
    if parsed_name_info:
        endDate = parsed_name_info[-1]
        end_time = float(endDate)
        start_time = end_time - duration
    else:
        start_time = 0.0
        end_time = 0.0
    return end_time, start_time
