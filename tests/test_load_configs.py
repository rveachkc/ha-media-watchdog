import os
import pprint
from typing import Self
from unittest import TestCase, mock

from ha_watchdog_libs.watchdog_intervals import WatchdogInterval
from ha_watchdog_libs.watchdog_rules import WatchdogRule
from ha_watchdog_libs.watchdog_script import HaMediaWatchdog

HERE = os.path.dirname(__file__)
CONFIG_FILE = os.path.join(HERE, "test_configs", "test_config_file.yml")


class TestConfigLoader(TestCase):
    @mock.patch("sys.argv", ["script_name", CONFIG_FILE])
    def setUp(self: Self):
        self.mwd = HaMediaWatchdog()

    def test_rule_configs(self: Self):
        self.assertTrue(os.path.isfile(CONFIG_FILE))
        self.assertEqual(
            os.path.abspath(CONFIG_FILE), os.path.abspath(self.mwd.args.config)
        )

        api_url, rules = self.mwd.read_config_from_file(self.mwd.args.config)
        self.assertIsInstance(api_url, str)

        pprint.pprint(rules)

        self.assertEqual(len(rules), 1)

        rule1 = rules[0]

        self.assertIsInstance(rule1, WatchdogRule)
        self.assertEqual(len(rule1.intervals), 2)

        for i in rule1.intervals:
            self.assertIsInstance(i, WatchdogInterval)
