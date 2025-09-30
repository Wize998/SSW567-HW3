import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch, Mock
import requests

import github_summary


def mk_resp(status=200, json_data=None):
    """
    Build a minimal response mock with .status_code, .json(), and .raise_for_status()
    """
    m = Mock()
    m.status_code = status

    if json_data is None:
        json_data = []
    m.json.return_value = json_data

    def raise_for_status():
        if status >= 400 and status != 409:
            raise requests.HTTPError(f"HTTP {status}")

    m.raise_for_status.side_effect = raise_for_status
    return m


class TestHw3bMocking(unittest.TestCase):
    def run_main(self, argv):

        buf = io.StringIO()
        with patch("sys.argv", argv), redirect_stdout(buf):
            code = github_summary.main()
        return code, buf.getvalue()

    @patch("requests.get")
    def test_happy_two_repos_with_one_conflict(self, mock_get):

        # 1) list repos
        repos = [{"name": "A"}, {"name": "B"}]
        # 2) commits for A (2 commits)
        commits_A = [{}, {}]
        # 3) commits for B (409 → treated as zero)
        mock_get.side_effect = [
            mk_resp(200, repos),
            mk_resp(200, commits_A),
            mk_resp(409),
        ]

        code, out = self.run_main(["github_summary.py", "someone"])
        self.assertEqual(code, 0)
        self.assertIn("Repo: A Number of commits: 2", out)
        self.assertIn("Repo: B Number of commits: 0", out)

    @patch("requests.get")
    def test_user_not_found_404(self, mock_get):
        """
        If the repos call returns 404, main() should print an error and return 1.
        """
        mock_get.side_effect = [mk_resp(404)]
        code, out = self.run_main(["github_summary.py", "no_such_user"])
        self.assertEqual(code, 1)
        self.assertIn("Error:", out)

    @patch("requests.get")
    def test_empty_repo_list(self, mock_get):
        """
        If the user has no repos, main() should print nothing and return 0.
        """
        mock_get.side_effect = [mk_resp(200, [])]
        code, out = self.run_main(["github_summary.py", "empty_user"])
        self.assertEqual(code, 0)
        self.assertNotIn("Repo:", out)


if __name__ == "__main__":
    unittest.main()
