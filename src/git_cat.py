#!/usr/bin/env python3
"""catfolio: picks your profile cat from your recent commits.

  python src/git_cat.py --login TU_USUARIO --coat orange --output-dir cat
  python src/git_cat.py --commits 5 --coat gray --output-dir cat      # no network
  python src/git_cat.py --state sleep --coat black                    # forced state

Standard library only. Writes <output-dir>/cat.gif, cat.json and preview.html.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COATS = ["gray", "orange", "calico", "siamese", "white", "tuxedo", "black", "tabby"]
STATES = ["auto", "sleep", "small", "medium", "large"]

QUERY = """query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){contributionsCollection(from:$from,to:$to){
    totalCommitContributions restrictedContributionsCount}}}"""


def level_for(commits):
    """0 sleep, 1-3 small, 4-9 medium, 10+ large (the more commits, the bigger)."""
    if commits <= 0:
        return "sleep"
    if commits <= 3:
        return "small"
    return "medium" if commits <= 9 else "large"


def count_commits(login, days, token):
    now = dt.datetime.now(dt.timezone.utc)
    fmt = "%Y-%m-%dT%H:%M:%SZ"
    body = json.dumps({"query": QUERY, "variables": {
        "login": login,
        "from": (now - dt.timedelta(days=days)).strftime(fmt),
        "to": now.strftime(fmt)}}).encode()
    req = urllib.request.Request("https://api.github.com/graphql", body,
                                 {"Authorization": f"bearer {token}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    if data.get("errors") or not (data.get("data") or {}).get("user"):
        sys.exit(f"catfolio: could not read the activity of {login}: {data.get('errors')}")
    c = data["data"]["user"]["contributionsCollection"]
    return c["totalCommitContributions"] + c["restrictedContributionsCount"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--login", default=os.environ.get("GITHUB_REPOSITORY_OWNER"))
    p.add_argument("--coat", default="orange", choices=COATS)
    p.add_argument("--state", default="auto", choices=STATES)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--commits", type=int, help="use this number instead of querying GitHub")
    p.add_argument("--output-dir", default="cat")
    p.add_argument("--token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    a = p.parse_args()

    commits = a.commits
    if a.state == "auto" and commits is None:
        if not (a.login and a.token):
            sys.exit("catfolio: --login and a token are required (or pass --commits / --state)")
        commits = count_commits(a.login, a.days, a.token)
    state = level_for(commits or 0) if a.state == "auto" else a.state

    src = os.path.join(ROOT, "dist", a.coat, f"{state}.gif")
    os.makedirs(a.output_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(a.output_dir, "cat.gif"))
    with open(os.path.join(a.output_dir, "cat.json"), "w") as f:
        json.dump({"coat": a.coat, "state": state, "commits": commits, "days": a.days}, f, indent=2)
    info = "" if commits is None else f" / {commits} commits in {a.days} days"
    with open(os.path.join(a.output_dir, "preview.html"), "w") as f:
        f.write('<!doctype html><meta charset="utf-8"><title>catfolio</title>'
                '<body style="font:14px system-ui;padding:16px"><img src="cat.gif">'
                f"<p>{a.coat} / {state}{info}</p>")
    print(f"{a.coat}/{state} (commits={commits}) -> {a.output_dir}/cat.gif")


if __name__ == "__main__":
    main()
