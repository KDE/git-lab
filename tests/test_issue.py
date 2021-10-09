import sys
import os
import unittest
from io import StringIO
from unittest.mock import MagicMock, patch

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../")

from lab.issue import IssueConnection


class MockIssueConnection(IssueConnection):
    """
    Subclass the original class to be able to override __init__.
    Otherwise IssueConnection would try to talk to the API.
    """

    def __init__(self, issue):
        self.issue = issue


class IssueTestCase(unittest.TestCase):

    def test_print_estimate(self):
        """
        Tests that the output for some sample data matches the expectation.
        """
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            mock_issue = MagicMock()
            mock_issue.title = "Fancy Title"
            mock_issue.attributes = {'time_stats': {
                'time_estimate': 520,
                'total_time_spent': 600,
                'human_time_estimate': '9m',
                'human_total_time_spent': '10m',
            }}
            issue = MockIssueConnection(mock_issue)
            issue.print_spent()

            mock_stdout.seek(0)
            self.assertEqual(
                mock_stdout.read(),
                '\x1b[1mFancy Title\x1b[0m has 10m tracked (estimated: \x1b[0;31m9m\x1b[0m)\n'
            )

    def test_print_spent(self):
        """
        Tests that the output for some sample data matches the expectation.
        """
        with patch("sys.stdout", new=StringIO()) as mock_stdout:
            mock_issue = MagicMock()
            mock_issue.title = "Fancy Title"
            mock_issue.attributes = {'time_stats': {
                'time_estimate': 28800,
                'total_time_spent': 25200,
                'human_time_estimate': '8h',
                'human_total_time_spent': '7h',
            }}
            issue = MockIssueConnection(mock_issue)
            issue.print_spent()

            mock_stdout.seek(0)
            self.assertEqual(
                mock_stdout.read(),
                '\x1b[1mFancy Title\x1b[0m has 7h tracked (estimated: \x1b[0;32m8h\x1b[0m)\n'
            )
