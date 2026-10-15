"""Commit counter for the most-commits-in-a-day attempt.

python commit.py 500      make 500 commits (each appends one line to log.txt)
python commit.py --count  show how many commits were made today
"""
import subprocess
import sys
from datetime import datetime
from pathlib import Path

HERE = Path(__file__).parent
LOG = HERE / "log.txt"


def git(*args):
    return subprocess.run(["git", "-C", str(HERE), *args], check=True,
                          capture_output=True, text=True).stdout


def today_count():
    since = datetime.now().strftime("%Y-%m-%d 00:00")
    out = git("rev-list", "--count", f"--since={since}", "HEAD") if has_commits() else "0"
    return int(out.strip())


def has_commits():
    return subprocess.run(["git", "-C", str(HERE), "rev-parse", "HEAD"],
                          capture_output=True).returncode == 0


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--count":
        print(f"commits today: {today_count()}")
        return
    n = int(sys.argv[1])
    start = today_count()
    with LOG.open("a", newline="\n") as f:
        for i in range(1, n + 1):
            num = start + i
            f.write(f"{num} {datetime.now().isoformat(timespec='milliseconds')}\n")
            f.flush()
            git("add", "log.txt")
            git("commit", "-q", "-m", f"commit {num}")
            if i % 100 == 0 or i == n:
                print(f"{num} today")
    print(f"done, commits today: {today_count()}")


if __name__ == "__main__":
    main()
