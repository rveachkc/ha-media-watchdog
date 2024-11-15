from typing import Self, Literal, Optional
from dataclasses import dataclass

@dataclass
class WatchdogRule:
    name: str
    action: Literal["warn", "stop", "home"]
    sources: Optional[list[str]] = None
    entity_ids: Optional[list[str]] = None

    def rule_applies(self: Self, entity_id: str, source_name: str) -> bool:

        return all(
            [
                bool(source_name),
                source_name != "Home",
                True if not self.entity_ids else (entity_id in self.entity_ids),
                True if not self.sources else (source_name in self.sources),
            ]
        )
