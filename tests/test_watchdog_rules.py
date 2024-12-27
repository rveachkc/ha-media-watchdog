from typing import Self
from unittest import TestCase

from ha_watchdog_libs.watchdog_rules import WatchdogRule


class TestRuleAppliesBasic(TestCase):
    def testBasicRule(self: Self):
        """
        With no inputs, this should apply to everything.
        """
        wr = WatchdogRule(name="TestRule", action="warn")

        self.assertTrue(wr.rule_applies(entity_id="my_cool_roku", source_name="rv_tv"))


class TestRuleAppliesScenarios(TestCase):
    KIDS_TV = "media_player.kids_watch_this_tv"
    ADULT_TV = "media_player.adult_only_tv"

    MATURE_SHOWS = "Naughty Shows Kids Shouldn't Watch"
    APPROVED_SHOWS = "OK Shows for Kids"

    def test_source_blacklist(self: Self):
        """
        This is a basic rule where we block a specific app from the kid tv
        We should allow it from other tv's in the home.
        """

        # basic tv rule preventing kids from watching bad shows
        wr = WatchdogRule(
            name="TestRule",
            action="warn",
            sources=[self.MATURE_SHOWS],
            entity_ids=[self.KIDS_TV],
        )

        # kids shouldn't watch this
        self.assertTrue(
            wr.rule_applies(
                entity_id=self.KIDS_TV,
                source_name=self.MATURE_SHOWS,
            )
        )

        # kids are ok to watch this
        self.assertFalse(
            wr.rule_applies(
                entity_id=self.KIDS_TV,
                source_name=self.APPROVED_SHOWS,
            )
        )

        # adult tv should not be restricted
        self.assertFalse(
            wr.rule_applies(
                entity_id=self.ADULT_TV,
                source_name=self.MATURE_SHOWS,
            )
        )

        # adults can watch kids tv too
        self.assertFalse(
            wr.rule_applies(
                entity_id=self.ADULT_TV,
                source_name=self.APPROVED_SHOWS,
            )
        )

    def test_source_whitelist(self: Self):
        """
        Another basic rule, but this only only allows specific apps on a specific tv
        TV's not in the entity id list should be whitelisted
        """

        # basic tv rule preventing kids from watching bad shows
        wr = WatchdogRule(
            name="TestRule",
            action="warn",
            sources_except=[self.APPROVED_SHOWS],
            entity_ids=[self.KIDS_TV],
        )

        # kids shouldn't watch this
        self.assertTrue(
            wr.rule_applies(
                entity_id=self.KIDS_TV,
                source_name=self.MATURE_SHOWS,
            )
        )

        # kids are ok to watch this
        self.assertFalse(
            wr.rule_applies(
                entity_id=self.KIDS_TV,
                source_name=self.APPROVED_SHOWS,
            )
        )

        # adult tv should not be restricted
        self.assertFalse(
            wr.rule_applies(
                entity_id=self.ADULT_TV,
                source_name=self.MATURE_SHOWS,
            )
        )

        # adults can watch kids tv too
        self.assertFalse(
            wr.rule_applies(
                entity_id=self.ADULT_TV,
                source_name=self.APPROVED_SHOWS,
            )
        )
