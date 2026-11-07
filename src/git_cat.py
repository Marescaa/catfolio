#!/usr/bin/env python3
"""catfolio: elige el gato de tu perfil segun tus commits de los ultimos dias.

  python src/git_cat.py --login TU_USUARIO --coat naranja --output-dir cat
  python src/git_cat.py --commits 5 --coat gris --output-dir cat      # sin red
  python src/git_cat.py --state sleep --coat negro                    # manual

Solo usa la libreria estandar. Escribe <output-dir>/cat.gif, cat.json y preview.html.
"""
import argparse
import datetime as dt
import json
import os
import shutil
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COATS = ["gris", "naranja", "calico", "siames", "blanco", "esmoquin", "negro", "atigrado"]
STATES = ["auto", "sleep", "calm", "happy", "joyful"]

QUERY = """query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){contributionsCollection(from:$from,to:$to){
    totalCommitContributions restrictedContributionsCount}}}"""


def level_for(commits):
    """0-2 calm, 3-6 happy, 7+ joyful. 'sleep' solo se elige a mano."""
    if commits <= 2:
        return "calm"
    return "happy" if commits <= 6 else "joyful"


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
        sys.exit(f"catfolio: no pude leer la actividad de {login}: {data.get('errors')}")
    c = data["data"]["user"]["contributionsCollection"]
    return c["totalCommitContributions"] + c["restrictedContributionsCount"]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--login", default=os.environ.get("GITHUB_REPOSITORY_OWNER"))
    p.add_argument("--coat", default="naranja", choices=COATS)
    p.add_argument("--state", default="auto", choices=STATES)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--commits", type=int, help="usar este numero en vez de consultar GitHub")
    p.add_argument("--output-dir", default="cat")
    p.add_argument("--token", default=os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN"))
    a = p.parse_args()

    commits = a.commits
    if a.state == "auto" and commits is None:
        if not (a.login and a.token):
            sys.exit("catfolio: faltan --login y token (o pasa --commits / --state)")
        commits = count_commits(a.login, a.days, a.token)
    state = level_for(commits or 0) if a.state == "auto" else a.state

    src = os.path.join(ROOT, "dist", a.coat, f"{state}.gif")
    os.makedirs(a.output_dir, exist_ok=True)
    shutil.copyfile(src, os.path.join(a.output_dir, "cat.gif"))
    with open(os.path.join(a.output_dir, "cat.json"), "w") as f:
        json.dump({"coat": a.coat, "state": state, "commits": commits, "days": a.days}, f, indent=2)
    info = "" if commits is None else f" / {commits} commits en {a.days} dias"
    with open(os.path.join(a.output_dir, "preview.html"), "w") as f:
        f.write('<!doctype html><meta charset="utf-8"><title>catfolio</title>'
                '<body style="font:14px system-ui;padding:16px"><img src="cat.gif">'
                f"<p>{a.coat} / {state}{info}</p>")
    print(f"{a.coat}/{state} (commits={commits}) -> {a.output_dir}/cat.gif")


if __name__ == "__main__":
    main()
