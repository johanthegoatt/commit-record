# commit-record

Going for the most commits in a single day.

```
python commit.py 1000     # make 1000 commits
python commit.py --fast 3000000  # same thing via git fast-import, minutes not days
python commit.py --count  # how many today
```

Each commit appends a numbered, timestamped line to `log.txt`, so the log doubles as proof of the run. In `--fast` mode each commit rewrites `count.txt` with its number and timestamp, and the run's lines are added to `log.txt` in one closing commit.
