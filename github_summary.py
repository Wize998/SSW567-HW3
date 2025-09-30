import sys, requests, json


def main():
    if len(sys.argv) != 2:
        print("Usage: python github_summary.py <github-username>")
        return 2

    user = sys.argv[1]
    base = "https://api.github.com"

    try:
        r = requests.get(f"{base}/users/{user}/repos", timeout=10)
        r.raise_for_status()
        repos = r.json()

        for repo in repos:
            name = repo.get("name")
            if not name:
                continue

            url = f"{base}/repos/{user}/{name}/commits?per_page=100"
            resp = requests.get(url, timeout=10)

            if resp.status_code == 409:
                count = 0
            else:
                resp.raise_for_status()
                count = len(resp.json())

            print(f"Repo: {name} Number of commits: {count}")

        return 0

    except requests.RequestException as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
