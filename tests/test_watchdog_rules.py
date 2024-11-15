from typing import Self
from unittest import TestCase
from ha_watchdog_libs.watchdog_rules import WatchdogRule

class TestRuleApplies(TestCase):

    def testBasicRule(self: Self):
        """
        With no inputs, this should apply to everything.
        """
        wr = WatchdogRule(name="TestRule", action="warn")

        self.assertTrue(
            wr.rule_applies(entity_id="my_cool_roku", source_name="rv_tv")
        )
