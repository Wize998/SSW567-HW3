import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch, Mock
import requests

import github_summary


def resp(code=200, json_list=None):
    m = Mock()
    m.status_code = code
    m.json.return_value = [] if json_list is None else json_list

    def _raise():
        if 400 <= code < 600 and code != 409:
            raise requests.HTTPError(f"{code}")

    m.raise_for_status.side_effect = _raise
    return m


class TestGithubSummarySimple(unittest.TestCase):
    @patch("github_summary.requests.get")
    def test_happy_path(self, get):
        get.side_effect = [
            resp(200, [{"name": "A"}, {"name": "B"}]),
            resp(200, [{}, {}]),
            resp(200, [{}, {}, {}]),
        ]
        out = io.StringIO()
        with patch("sys.argv", ["x", "someone"]), redirect_stdout(out):
            code = github_summary.main()
        self.assertEqual(code, 0)
        self.assertIn("Repo: A Number of commits: 2", out.getvalue())
        self.assertIn("Repo: B Number of commits: 3", out.getvalue())

        # path test go through

    @patch("github_summary.requests.get")
    def test_empty_repo_409_means_zero(self, get):
        get.side_effect = [
            resp(200, [{"name": "Empty"}]),
            resp(409),
        ]
        out = io.StringIO()
        with patch("sys.argv", ["x", "someone"]), redirect_stdout(out):
            code = github_summary.main()
        self.assertEqual(code, 0)
        self.assertIn("Repo: Empty Number of commits: 0", out.getvalue())
        # 409 to 0

    @patch("github_summary.requests.get")
    def test_user_not_found_404_is_error(self, get):
        get.side_effect = [resp(404)]
        out = io.StringIO()
        with patch("sys.argv", ["x", "baduser"]), redirect_stdout(out):
            code = github_summary.main()
        self.assertEqual(code, 1)
        self.assertIn("Error:", out.getvalue())

        # 404 error test


if __name__ == "__main__":
    unittest.main()


if __name__ == "__main__":
    unittest.main()

