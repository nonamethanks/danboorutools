import datetime

import pytz
from dateutil import parser


def timestamp_from_string(time_value: str | int | float | datetime.datetime, backup_tz: str | None = None) -> datetime.datetime:
    """Parse an int or str into a datetime."""
    if isinstance(time_value, (int, float)) or (isinstance(time_value, str) and time_value.isnumeric()):
        # unix timestamp
        while len(str(int(time_value))) > 10:
            time_value = float(time_value) / 10

        tz = pytz.timezone(backup_tz) if backup_tz else pytz.UTC
        timestamp = datetime.datetime.fromtimestamp(float(time_value), tz=tz)
    elif isinstance(time_value, datetime.datetime):
        timestamp = time_value
    else:
        timestamp = parser.parse(time_value)

    if not timestamp.tzinfo:
        tz = pytz.timezone(backup_tz) if backup_tz else pytz.UTC
        timestamp = timestamp.replace(tzinfo=tz)

    return timestamp
