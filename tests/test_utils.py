#!/usr/bin/env python3

import os.path
import sys
import unittest
from datetime import datetime, timedelta, timezone

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from lab.utils import Utils
from lab.pipelines import PipelineStatus
from lab.issue import is_valid_time_str


class UtilsTest(unittest.TestCase):
    def test_gitlab_instance_url(self):
        # https
        repos = (
            "git@invent.kde.org:KDE/kaidan.git",
            "ssh://git@invent.kde.org/KDE/kaidan.git" "https://invent.kde.org/KDE/kaidan",
            "git://invent.kde.org/KDE/kaidan",
        )

        for repo in repos:
            url = Utils.gitlab_instance_url(repo)
            self.assertEqual(url, "https://invent.kde.org")

        # http
        url = Utils.gitlab_instance_url("http://invent.kde.org/KDE/kaidan")
        self.assertEqual(url, "http://invent.kde.org")

    def test_normalize_url(self):
        scp_url: str = "git@invent.kde.org:KDE/kaidan.git"
        url = Utils.normalize_url(scp_url)
        self.assertEqual(url, "ssh://git@invent.kde.org/KDE/kaidan.git")

        http_url: str = "https://invent.kde.org/KDE/kaidan.git"
        url = Utils.normalize_url(http_url)
        self.assertEqual(url, "https://invent.kde.org/KDE/kaidan.git")

    def test_str_id_for_url(self):
        url: str = "ssh://git@invent.kde.org/KDE/kaidan.git"

        str_id: str = Utils.str_id_for_url(url)

        self.assertEqual(str_id, "KDE/kaidan")

        # This is not a valid repository name for KDE invent, though
        url = "ssh://git@invent.kde.org/KDE/kaidan%.git"
        str_id = Utils.str_id_for_url(url)
        self.assertEqual(str_id, "KDE/kaidan%")

    def test_ssh_url_from_http(self):
        url: str = "http://invent.kde.org/KDE/kaidan"

        ssh_url: str = Utils.ssh_url_from_http(url)

        self.assertEqual(ssh_url, "ssh://git@invent.kde.org/KDE/kaidan")

    def test_id_url_ending_on_slash(self):
        url: str = "https://invent.kde.org/network/kaidan/"

        str_id: str = Utils.str_id_for_url(url)

        self.assertEqual(str_id, "network/kaidan")

    def test_pretty_date(self) -> None:
        ref_date = datetime(2020, 1, 1)
        fmt = "%Y-%m-%dT%H:%M:%S.%fZ"

        iso_date_1 = ref_date + timedelta(seconds=9)
        self.assertEqual(Utils.pretty_date(ref_date.strftime(fmt), iso_date_1), "just now")

        iso_date_1 = ref_date + timedelta(seconds=59)
        self.assertEqual(Utils.pretty_date(ref_date.strftime(fmt), iso_date_1), "59 seconds ago")

        iso_date_1 = ref_date + timedelta(seconds=5 * 60)
        self.assertEqual(Utils.pretty_date(ref_date.strftime(fmt), iso_date_1), "5 minutes ago")

        iso_date_1 = ref_date + timedelta(seconds=60 * 60)
        self.assertEqual(Utils.pretty_date(ref_date.strftime(fmt), iso_date_1), "an hour ago")

        iso_date_1 = ref_date + timedelta(seconds=24 * 60 * 60)
        self.assertEqual(Utils.pretty_date(ref_date.strftime(fmt), iso_date_1), "Yesterday")

        iso_date_1 = ref_date + timedelta(seconds=14 * 24 * 60 * 60)
        self.assertEqual(Utils.pretty_date(ref_date.strftime(fmt), iso_date_1), "2 weeks ago")

    def test_timezone_awareness_of_pretty_date(self) -> None:
        ref_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        fmt = "%Y-%m-%dT%H:%M:%S.%fZ"

        iso_date_1 = ref_date + timedelta(seconds=9)
        self.assertEqual(Utils.pretty_date(ref_date.replace(tzinfo=None).strftime(fmt), iso_date_1), "just now")

    def test_pretty_time_delta(self) -> None:
        delta = timedelta(days=1, hours=12, minutes=10, seconds=20)
        tot_sec = int(delta.total_seconds())
        self.assertEqual(Utils.pretty_time_delta(tot_sec), "1d 12h 10m 20s")

        delta = timedelta(hours=23, minutes=57, seconds=0)
        tot_sec = int(delta.total_seconds())
        self.assertEqual(Utils.pretty_time_delta(tot_sec), "23h 57m 0s")

        delta = timedelta(minutes=2, seconds=59)
        tot_sec = int(delta.total_seconds())
        self.assertEqual(Utils.pretty_time_delta(tot_sec), "2m 59s")

        delta = timedelta(seconds=3)
        tot_sec = int(delta.total_seconds())
        self.assertEqual(Utils.pretty_time_delta(tot_sec), "3s")

        # Also test sign
        delta = timedelta(seconds=3)
        tot_sec = - int(delta.total_seconds())
        self.assertEqual(Utils.pretty_time_delta(tot_sec), "3s")


class PipelineTest(unittest.TestCase):

    def test_enum_with_supported_status(self):
        self.assertEqual(PipelineStatus("waiting_for_resource"), PipelineStatus.WAITING)
        self.assertEqual(PipelineStatus("pending"), PipelineStatus.PENDING)
        self.assertEqual(PipelineStatus("running"), PipelineStatus.RUNNING)
        self.assertEqual(PipelineStatus("success"), PipelineStatus.SUCCESS)
        self.assertEqual(PipelineStatus("failed"), PipelineStatus.FAILED)
        self.assertEqual(PipelineStatus("canceled"), PipelineStatus.CANCELED)
        self.assertEqual(PipelineStatus("scheduled"), PipelineStatus.SCHEDULED)

    def test_color_formatting(self):
        self.assertEqual(PipelineStatus.SUCCESS.formatted, '\x1b[0;32msuccess\x1b[0m')
        self.assertEqual(PipelineStatus.FAILED.formatted, '\x1b[0;31mfailed\x1b[0m')
        self.assertEqual(PipelineStatus.RUNNING.formatted, '\x1b[0;34mrunning\x1b[0m')
        self.assertEqual(PipelineStatus.CANCELED.formatted, '\x1b[0;95mcanceled\x1b[0m')
        self.assertEqual(PipelineStatus.PENDING.formatted, '\x1b[0;34mpending\x1b[0m')
        self.assertEqual(PipelineStatus.WAITING.formatted, '\x1b[0;33mwaiting_for_resource\x1b[0m')

        # Make sure that status with no associated color are not changed
        self.assertEqual(PipelineStatus.SKIPPED.formatted, "skipped")

    def test_finished(self):
        self.assertFalse(PipelineStatus.WAITING.finished)
        self.assertFalse(PipelineStatus.PENDING.finished)
        self.assertFalse(PipelineStatus.RUNNING.finished)
        self.assertFalse(PipelineStatus.SCHEDULED.finished)

        self.assertTrue(PipelineStatus.SUCCESS.finished)
        self.assertTrue(PipelineStatus.FAILED.finished)
        self.assertTrue(PipelineStatus.CANCELED.finished)
        self.assertTrue(PipelineStatus.SKIPPED.finished)


class TestTimeTracking(unittest.TestCase):

    def test_regex(self):
        self.assertTrue(is_valid_time_str("1mo2w4d10h2m"))
        self.assertTrue(is_valid_time_str("2w4d10h2m"))
        self.assertTrue(is_valid_time_str("4d10h2m"))
        self.assertTrue(is_valid_time_str("10h2m"))
        self.assertTrue(is_valid_time_str("2m"))
        self.assertTrue(is_valid_time_str("10m"))
        self.assertTrue(is_valid_time_str("12h"))
        self.assertTrue(is_valid_time_str("5d"))
        self.assertTrue(is_valid_time_str("10w"))
        self.assertTrue(is_valid_time_str("8m"))

        self.assertFalse(is_valid_time_str("w"))
        self.assertFalse(is_valid_time_str("mo"))
        self.assertFalse(is_valid_time_str("d"))
        self.assertFalse(is_valid_time_str("h"))
        self.assertFalse(is_valid_time_str("m"))
        self.assertFalse(is_valid_time_str("100"))
        self.assertFalse(is_valid_time_str("100p"))
        self.assertFalse(is_valid_time_str("100wof"))
        self.assertFalse(is_valid_time_str("bar1foo"))


if __name__ == "__main__":
    unittest.main()
