"""Commit counter for the most-commits-in-a-day attempt.

python commit.py 500          make 500 commits (each appends one line to log.txt)
python commit.py --fast 500   same count via git fast-import, for runs in the millions
python commit.py --count      show how many commits were made today
"""
import subprocess
import sys
import time
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


def fast(n):
    """Each commit rewrites count.txt; the run's lines land in log.txt in one closing commit."""
    if git("status", "--porcelain"):
        sys.exit("commit or stash your changes first")
    start = today_count()
    branch = git("symbolic-ref", "HEAD").strip()
    parent = git("rev-parse", "HEAD").strip()
    who = f"{git('config', 'user.name').strip()} <{git('config', 'user.email').strip()}>"
    off = time.localtime().tm_gmtoff // 60
    tz = f"{'+' if off >= 0 else '-'}{abs(off) // 60:02d}{abs(off) % 60:02d}"
    lines = []
    fi = subprocess.Popen(["git", "-C", str(HERE), "fast-import", "--quiet"],
                          stdin=subprocess.PIPE)
    out = fi.stdin
    for i in range(1, n + 1):
        num = start + i
        now = time.time()
        line = f"{num} {datetime.fromtimestamp(now).isoformat(timespec='milliseconds')}\n"
        lines.append(line)
        msg = f"commit {num}\n".encode()
        body = line.encode()
        out.write(f"commit {branch}\ncommitter {who} {int(now)} {tz}\n".encode())
        out.write(b"data %d\n%s" % (len(msg), msg))
        out.write(f"from {parent}\n".encode() if i == 1 else b"")
        out.write(b"M 644 inline count.txt\ndata %d\n%s\n" % (len(body), body))
        if i % 100_000 == 0 or i == n:
            print(f"{num} today")
    out.close()
    if fi.wait():
        sys.exit("fast-import failed, branch left unchanged")
    git("reset", "-q", "--hard")
    with LOG.open("a", newline="\n") as f:
        f.writelines(lines)
    git("add", "log.txt")
    git("commit", "-q", "-m", f"log commits {start + 1}-{start + n}")
    print(f"done, commits today: {today_count()}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--count":
        print(f"commits today: {today_count()}")
        return
    if sys.argv[1] == "--fast":
        fast(int(sys.argv[2]))
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
