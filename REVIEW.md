# Review session runbook (scheduled Claude session, about twice a week)

Budget: keep this session small, about 25 tool calls at most. The user is on a shared usage
plan. Prefer one well-reasoned change over many small ones.

1. `git pull`. Read `state/summary.md`, the last ~40 lines of `JOURNAL.md`, and the
   `STRATEGY.md` open questions. Skim the last week of `state/metrics.csv` (`tail -n 90`).
2. **Health check.** Is the newest "run …" commit less than 6 hours old? Does the data-health
   table show any failures, or notes that keep repeating? If runs are failing, check the Actions
   logs (GitHub MCP `actions_list` / `get_job_logs`). Fixing a broken pipeline comes before
   anything else.
3. **Performance.** Compare net worth and realized P&L with the previous journal entry. Look at
   the worst items: are we losing to fees, to stale stock, or to bad picks? Is cash sitting idle
   while candidates go unused (raise sizing), or are we running out of slots or time?
4. **Decide at most 1–2 changes** (`config.toml` parameters or code), each with a hypothesis
   and a way to tell whether it worked. Don't retune something before it has had about 3 days
   to show results.
5. `python -m pytest -q`, commit with a clear message, push to the default branch.
6. Append a `JOURNAL.md` entry: date, numbers (net worth, % change, realized), what you
   changed, and why, plus what to check next time. Keep it under 15 lines.

Never edit the files under `state/` by hand, except for a deliberate reset that the journal
records.
