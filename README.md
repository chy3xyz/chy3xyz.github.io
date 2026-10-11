# chy3xyz.github.io

Personal site for [chy3xyz](https://github.com/chy3xyz). Serves at <https://chy3xyz.github.io/>.

## Layout

| File | Purpose |
|---|---|
| `index.template.html` | Source template with `__FEATURED__` / `__ALL__` / `__COUNT__` placeholders |
| `index.html` | Generated output — **do not edit by hand** |
| `update.py` | Pulls the live repo list from the GitHub API and rebuilds `index.html` |
| `.nojekyll` | Keeps Jekyll from swallowing `_`-prefixed paths |

## Updating

```bash
python3 update.py
git commit -am "refresh repo list" && git push
```

Requires `gh auth login` with `read:org` scope. To change which projects appear in the
Featured grid, edit the `FEATURED` list at the top of `update.py`.

## Deployment

Pages serves the `main` branch root directly (build type: *Deploy from a branch*).
Every push to `main` goes live — no CI step, nothing to break.

Optional: if you'd rather have the list refresh on its own, add a workflow that runs
`python3 update.py` and force-pushes to `gh-pages`, then switch the Pages build type
to *GitHub Actions*.