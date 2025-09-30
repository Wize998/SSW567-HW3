# test_hw3b_mocking.py
import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch, Mock
import requests

import github_summary  # your script that defines main()


def fake_resp(status=200, payload=None):
    """Minimal Response double with .status_code/.json()/.raise_for_status()."""
    m = Mock()
    m.status_code = status
    m.json.return_value = [] if payload is None else payload

    def _raise():
        # emulate requests behavior: raise on 4xx/5xx EXCEPT 409 (empty repo)
        if 400 <= status < 600 and status != 409:
            raise requests.HTTPError(f"{status}")

    m.raise_for_status.side_effect = _raise
    return m


class TestMocking(unittest.TestCase):
    @patch("github_summary.requests.get")
    def test_happy_path_two_repos(self, get):
        # repos: A, B; commits: A=2, B=3
        get.side_effect = [
            fake_resp(200, [{"name": "A"}, {"name": "B"}]),
            fake_resp(200, [{}, {}]),
            fake_resp(200, [{}, {}, {}]),
        ]
        buf = io.StringIO()
        with patch("sys.argv", ["prog", "someone"]), redirect_stdout(buf):
            code = github_summary.main()
        out = buf.getvalue()
        self.assertEqual(code, 0)
        self.assertIn("Repo: A Number of commits: 2", out)
        self.assertIn("Repo: B Number of commits: 3", out)

    @patch("github_summary.requests.get")
    def test_empty_repo_shows_zero_on_409(self, get):
        get.side_effect = [
            fake_resp(200, [{"name": "Empty"}]),
            fake_resp(409),  # empty repo signal
        ]
        buf = io.StringIO()
        with patch("sys.argv", ["prog", "someone"]), redirect_stdout(buf):
            code = github_summary.main()
        self.assertEqual(code, 0)
        self.assertIn("Repo: Empty Number of commits: 0", buf.getvalue())

    @patch("github_summary.requests.get")
    def test_user_not_found_404(self, get):
        get.side_effect = [fake_resp(404)]
        buf = io.StringIO()
        with patch("sys.argv", ["prog", "nope"]), redirect_stdout(buf):
            code = github_summary.main()
        self.assertEqual(code, 1)
        self.assertIn("Error:", buf.getvalue())

    @patch("github_summary.requests.get")
    def test_timeout(self, get):
        get.side_effect = requests.Timeout("too slow")
        buf = io.StringIO()
        with patch("sys.argv", ["prog", "whoever"]), redirect_stdout(buf):
            code = github_summary.main()
        self.assertEqual(code, 1)
        self.assertIn("Error:", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
