import zoneinfo
from datetime import datetime


def get_local_time(timezone: str = "UTC") -> str:
    """Returns the current time in the given timezone as ISO 8601 string."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Invalid timezone: {timezone}"
    now = datetime.now(tz)
    return now.strftime("%A, %B %d, %Y %I:%M %p %Z")


if __name__ == "__main__":
    print(get_local_time(timezone="America/Los_Angeles"))
