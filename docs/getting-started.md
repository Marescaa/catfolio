# Getting started

Catfolio has three ways to run: the GitHub Action in a profile workflow, the
command line, and a rebuild of the scenes. Pick the first for a profile README.

## The Action in a profile workflow

1. In your profile repository (`<you>/<you>`), copy
   [`examples/workflow.yml`](../examples/workflow.yml) to
   `.github/workflows/cat.yml`. Change `Marescaa/catfolio@v3` to the account that
   hosts this repository if you forked it.
2. Add the cat to your `README.md`:

   ```html
   <p align="center"><img src="cat/cat.gif" width="480" alt="My cat" /></p>
   ```

3. Run the workflow once by hand: **Actions → Cat → Run workflow**. After that
   it refreshes every night.

The workflow needs `contents: write` so it can commit the new GIF. To change the
coat for good, edit the `coat` input in the workflow, or set a repository
variable named `CAT_COAT`.

## The command line

```bash
python src/git_cat.py --login <you> --coat gray --output-dir cat   # reads GITHUB_TOKEN
python src/git_cat.py --commits 5 --coat black --output-dir cat    # no network
python src/git_cat.py --state sleep --coat calico --output-dir cat
```

It writes `cat.gif`, `cat.json` (the coat, state, and commit count), and
`preview.html` into the output folder. It uses only the standard library.

## Rebuilding the scenes

`dist/` is rendered from the sprites in `assets/`. To change the route, the
sizes, or the canvas, edit `tools/render.py` and run:

```bash
pip install -r requirements-dev.txt
python tools/render.py            # every coat
python tools/render.py orange    # one coat
python tools/sheet.py             # the coat sheets in docs/
```

## How the state is picked

Catfolio counts your commits over the last `days` days (7 by default), including
private ones if your profile shows them. The count maps to a state:

| Commits | State |
|---|---|
| 0 | `sleep` |
| 1 to 3 | `small` |
| 4 to 9 | `medium` |
| 10 or more | `large` |

The thresholds live in `level_for` in `src/git_cat.py`.
