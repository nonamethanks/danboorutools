import datetime
from zoneinfo import ZoneInfo

from dateutil import parser


def datetime_from_string(time_value: str | float | datetime.datetime, backup_tz: str | None = None) -> datetime.datetime:
    """Parse an int or str into a datetime."""

    timezone = ZoneInfo(name=backup_tz) if backup_tz else datetime.UTC

    if isinstance(time_value, int | float) or (isinstance(time_value, str) and time_value.isnumeric()):
        # unix timestamp
        while len(str(int(time_value))) > 10:
            time_value = float(time_value) / 10

        timestamp = datetime.datetime.fromtimestamp(float(time_value), tz=timezone)
    elif isinstance(time_value, datetime.datetime):
        timestamp = time_value
    else:
        timestamp = parser.parse(time_value)

    if not timestamp.tzinfo:
        timestamp = timestamp.replace(tzinfo=timezone)

    return timestamp
