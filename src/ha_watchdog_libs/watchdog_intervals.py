import datetime
from calendar import day_abbr, day_name
from dataclasses import dataclass, field
from typing import Iterable, Optional, Self


def parse_time(time_str: str) -> datetime.time:
    """
    Function to be used when parsing time in the HH:MM format
    Extra logic to convert 24:00 to time.max
    """
    if time_str == "24:00":
        return datetime.time.max

    return datetime.datetime.strptime(time_str, "%H:%M").time()


@dataclass
class WatchdogInterval:
    start_time: str
    end_time: str
    days: Optional[Iterable[str]] = field(default_factory=list)

    start_obj: Optional[datetime.time] = field(init=False)
    end_obj: Optional[datetime.time] = field(init=False)

    def __post_init__(self: Self):
        self.start_obj = parse_time(self.start_time)
        self.end_obj = parse_time(self.end_time)
        self.days = set(map(lambda x: x.lower(), self.days))

    def get_current_day_set(self: Self) -> set[str]:
        """
        Returns a set for both the week full name and abbreviation in lowercase
        """
        today_int = datetime.date.today().weekday()
        return {day_abbr[today_int].lower(), day_name[today_int].lower()}

    def is_active(self: Self) -> bool:
        """
        Boolean value indicating whether or not the interval is active
        """
        return all(
            [
                True
                if not self.days
                else bool(self.days.intersection(self.get_current_day_set())),
                self.start_obj <= datetime.datetime.now().time() <= self.end_obj,
            ]
        )
