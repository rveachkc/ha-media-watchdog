from typing import Self
from unittest import TestCase

from freezegun import freeze_time

from ha_watchdog_libs.watchdog_intervals import WatchdogInterval
from ha_watchdog_libs.watchdog_rules import WatchdogRule


class TestIntervalRule(TestCase):
    KIDS_TV = "media_player.kids_watch_this_tv"
    WIND_UP_SHOWS = "Funny Stuff that'll keep them laughing all night"
    CALM_SHOWS = "Boring Stuff to help sleep"

    wr = WatchdogRule(
        name="TestIntervalRule",
        action="warn",
        sources=[WIND_UP_SHOWS],
        entity_ids=[KIDS_TV],
        intervals=[
            WatchdogInterval(
                start_time="21:00",
                end_time="24:00",
                days=["Sun", "Mon", "Tue", "Wed", "Thu"],
            ),
            WatchdogInterval(
                start_time="22:00",
                end_time="24:00",
                days=["Friday", "Saturday"],
            ),
        ],
    )

    @freeze_time("2024-12-26 12:30")
    def test_thu_early(self: Self):
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.WIND_UP_SHOWS)
        )
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.CALM_SHOWS)
        )

    @freeze_time("2024-12-26 21:30")
    def test_thu_late(self: Self):
        self.assertTrue(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.WIND_UP_SHOWS)
        )
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.CALM_SHOWS)
        )

    @freeze_time("2024-12-26 23:30")
    def test_thu_really_late(self: Self):
        self.assertTrue(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.WIND_UP_SHOWS)
        )
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.CALM_SHOWS)
        )

    @freeze_time("2024-12-27 12:30")
    def test_fri_early(self: Self):
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.WIND_UP_SHOWS)
        )
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.CALM_SHOWS)
        )

    @freeze_time("2024-12-27 21:30")
    def test_fri_late(self: Self):
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.WIND_UP_SHOWS)
        )
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.CALM_SHOWS)
        )

    @freeze_time("2024-12-27 23:30")
    def test_fri_really_late(self: Self):
        self.assertTrue(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.WIND_UP_SHOWS)
        )
        self.assertFalse(
            self.wr.rule_applies(entity_id=self.KIDS_TV, source_name=self.CALM_SHOWS)
        )
