from typing import Self, Literal, Optional
from dataclasses import dataclass, field

from ha_watchdog_libs.watchdog_intervals import WatchdogInterval

@dataclass
class WatchdogRule:
    name: str
    action: Literal["warn", "stop", "home"]
    sources: Optional[list[str]] = field(default_factory=list)
    sources_except: Optional[list[str]] = field(default_factory=list)
    entity_ids: Optional[list[str]] = field(default_factory=list)
    intervals: Optional[list[WatchdogInterval]] = field(default_factory=list)

    def rule_applies(self: Self, entity_id: str, source_name: str) -> bool:

        return all(
            [
                bool(source_name),
                source_name != "Home",
                True if not self.entity_ids else (entity_id in self.entity_ids),
                True if not self.sources else (source_name in self.sources),
                True if not self.sources_except else (source_name not in self.sources_except),
                True if not self.intervals else any(
                    map(
                        lambda x: x.is_active(),
                        self.intervals,
                    )
                )
            ]
        )
