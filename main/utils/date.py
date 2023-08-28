import datetime
import pytz

from django.conf import settings

local_tz = pytz.timezone(settings.TIME_ZONE)


def utc_to_local(utc_dt):
    """
        datetime ийг timezone болгох нь
    """
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def date_str_to_datetime(date_string, format="%Y-%m-%d"):
    """ string date ийг datetime instance болгох """
    return datetime.datetime.strptime(date_string, format)
