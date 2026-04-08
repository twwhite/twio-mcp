import zoneinfo
from datetime import datetime



def cmd_get_time(timezone: str = "America/Los_Angeles", **kwargs) -> str:
    """Returns the current time in the given timezone as ISO 8601 string."""
    try:
        tz = zoneinfo.ZoneInfo(timezone)
    except zoneinfo.ZoneInfoNotFoundError:
        return f"Invalid timezone: {timezone}"
    now = datetime.now(tz)
    return now.strftime("%A, %B %d, %Y %I:%M %p %Z")


if __name__ == "__main__":
    print(cmd_get_time(timezone="America/Los_Angeles"))
