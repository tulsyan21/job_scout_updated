# Job Scout

Weekly job-scouting agent. Runtime = Claude Code (Pro plan, no API key needed).
Deterministic fetching/filtering/state in Python; Claude Code does only scoring + drafts.

## One-time setup (10 minutes)
1. Put this folder somewhere permanent (e.g. ~/projects/job-scout).
2. `pip install pyyaml`
3. `cd job-scout && git init && git add -A && git commit -m "init"`
   (Optional but recommended: create a private GitHub repo and `git push` for backup.)
4. Open Claude Code here: `claude`
5. First session, say: **"verify watchlist"** — it runs `fetch.py --verify`, fixes broken
   ATS tokens, marks verified ones. All tokens in watchlist.yaml are guesses until this runs.
6. Merge your old claude.md content into `profile.md`. Red-line `config/watchlist.yaml`
   (Cred verdict is provisionally `fail` — confirm or overturn).
7. Calibration: say **"recalibrate"** — it scores your five anchor roles and reports drift.

## Weekly run (~2 min of your attention)
```
cd job-scout && claude
> run weekly scan
```
Read the digest in `digests/`, fill research checklists for anything you'll pursue,
copy outreach drafts from `outreach/` if any role hit 80+. Nothing is ever sent automatically.

## Files
- CLAUDE.md — the agent's operating manual (Claude Code reads this automatically)
- config/rubric.md — scoring rubric v3 (do not edit casually; use "recalibrate")
- config/watchlist.yaml — approved companies + metadata
- profile.md — your evidence base for scoring context and outreach drafts
- src/fetch.py — deterministic fetcher (no LLM calls)
- state/jobs.json — permanent memory; never delete
- digests/, outreach/ — weekly outputs
