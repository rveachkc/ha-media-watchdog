from dataclasses import dataclass, field
from typing import Literal, Optional, Self, Union

from ha_watchdog_libs.watchdog_intervals import WatchdogInterval


@dataclass
class WatchdogRule:
    name: str
    action: Literal["warn", "stop", "home"]
    sources: Optional[list[str]] = field(default_factory=list)
    sources_except: Optional[list[str]] = field(default_factory=list)
    entity_ids: Optional[list[str]] = field(default_factory=list)
    intervals: Optional[list[dict]] = field(default_factory=list)

    @staticmethod
    def __dict_to_interval(
        interval_in: Union[dict, WatchdogInterval],
    ) -> WatchdogInterval:
        """Helper function for the post init"""
        if isinstance(interval_in, dict):
            return WatchdogInterval(**interval_in)
        return interval_in

    def __post_init__(self: Self):
        """Yaml intervals are in dictionary. This converts them to the object"""
        self.intervals = [self.__dict_to_interval(x) for x in self.intervals]

    def rule_applies(self: Self, entity_id: str, source_name: str) -> bool:
        """
        Does the watchdog rule apply for entity and source?
        """
        return all(
            [
                bool(source_name),
                source_name != "Home",
                True if not self.entity_ids else (entity_id in self.entity_ids),
                True if not self.sources else (source_name in self.sources),
                True
                if not self.sources_except
                else (source_name not in self.sources_except),
                True
                if not self.intervals
                else any(
                    map(
                        lambda x: x.is_active(),
                        self.intervals,
                    )
                ),
            ]
        )
