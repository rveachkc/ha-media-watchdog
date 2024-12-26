import datetime
from typing import Self
from unittest import TestCase

from freezegun import freeze_time

from ha_watchdog_libs.watchdog_intervals import WatchdogInterval


class TestInteralBasic(TestCase):
    """
    Tests for a basic interval with a start and end time mid-day
    """

    WI = WatchdogInterval(
        start_time="21:00",
        end_time="22:00",
    )

    def test_data_types(self: Self):
        self.assertIsInstance(self.WI.end_obj, datetime.time)
        self.assertIsInstance(self.WI.start_obj, datetime.time)
        self.assertIsInstance(self.WI.days, set)
        self.assertEqual(len(self.WI.days), 0)

    @freeze_time("2024-12-26 21:30")
    def test_expect_positive(self: Self):
        self.assertTrue(self.WI.is_active())

    @freeze_time("2024-12-26 12:30")
    def test_expect_negative(self: Self):
        self.assertFalse(self.WI.is_active())

    @freeze_time("2024-12-26 21:00")
    def test_edge_begin(self: Self):
        self.assertTrue(self.WI.is_active())

    @freeze_time("2024-12-26 22:00")
    def test_edge_end(self: Self):
        self.assertTrue(self.WI.is_active())


class TestInteralUntilMidnight(TestCase):
    """
    Tests for a time interval defined to end at the end of the day, using 24:00 for that
    """

    WI = WatchdogInterval(
        start_time="21:00",
        end_time="24:00",
    )

    def test_data_types(self: Self):
        self.assertIsInstance(self.WI.end_obj, datetime.time)
        self.assertEqual(self.WI.end_obj, datetime.time.max)
        self.assertIsInstance(self.WI.start_obj, datetime.time)
        self.assertIsInstance(self.WI.days, set)
        self.assertEqual(len(self.WI.days), 0)

    @freeze_time("2024-12-26 23:30")
    def test_expect_positive(self: Self):
        self.assertTrue(self.WI.is_active())

    @freeze_time("2024-12-26 12:30")
    def test_expect_negative(self: Self):
        self.assertFalse(self.WI.is_active())

    @freeze_time("2024-12-26 23:59")
    def test_edge_begin(self: Self):
        self.assertTrue(self.WI.is_active())


class TestWithWeekdays(TestCase):
    """
    Tests including weekdays
    """

    WI = WatchdogInterval(
        start_time="21:00",
        end_time="24:00",
        days=[
            "Mon",
            "Tuesday",
        ],
    )

    def test_data_types(self: Self):
        self.assertIsInstance(self.WI.end_obj, datetime.time)
        self.assertEqual(self.WI.end_obj, datetime.time.max)
        self.assertIsInstance(self.WI.start_obj, datetime.time)
        self.assertIsInstance(self.WI.days, set)
        self.assertEqual(len(self.WI.days), 2)

        # we should pre-convert everything to lowercase on init
        for i in self.WI.days:
            self.assertEqual(i, i.lower())

    @freeze_time("2024-12-23 12:00")
    def test_mon_noon(self: Self):
        self.assertFalse(self.WI.is_active())

    @freeze_time("2024-12-23 23:00")
    def test_mon_2300(self: Self):
        self.assertTrue(self.WI.is_active())

    @freeze_time("2024-12-24 12:00")
    def test_tue_noon(self: Self):
        self.assertFalse(self.WI.is_active())

    @freeze_time("2024-12-24 23:00")
    def test_tue_2300(self: Self):
        self.assertTrue(self.WI.is_active())

    @freeze_time("2024-12-25 12:00")
    def test_wed_noon(self: Self):
        self.assertFalse(self.WI.is_active())

    @freeze_time("2024-12-25 23:00")
    def test_wed_2300(self: Self):
        self.assertFalse(self.WI.is_active())
