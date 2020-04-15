#!/usr/bin/env python3

import unittest

from lab.utils import Utils

class UtilsTest(unittest.TestCase):
    def test_gitlab_instance_url(self):
        # https
        repos = ("git@invent.kde.org:KDE/kaidan.git",
                 "ssh://git@invent.kde.org/KDE/kaidan.git"
                 "https://invent.kde.org/KDE/kaidan",
                 "git://invent.kde.org/KDE/kaidan")

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

        self.assertEqual(str_id, "KDE%2Fkaidan")

if __name__ == "__main__":
    unittest.main()
