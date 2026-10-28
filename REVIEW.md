# Review session runbook (scheduled Claude session, about twice a week)

Budget: keep this session small, about 25 tool calls at most. The user is on a shared usage
plan. Prefer one well-reasoned change over many small ones.

1. `git pull`. Read `state/summary.md`, the last ~40 lines of `JOURNAL.md`, and the
   `STRATEGY.md` open questions. Skim the last week of `state/metrics.csv` (`tail -n 90`).
2. **Health check.** Is the newest "run …" commit less than 6 hours old? Does the data-health
   table show any failures, or notes that keep repeating? If runs are failing, check the Actions
   logs (GitHub MCP `actions_list` / `get_job_logs`). Fixing a broken pipeline comes before
   anything else.
3. **Calibration (first review of each week).** `python -m trader.calibrate jita` and the import
   hub: the median inferred/official ratio should be stable and below 1 (station volume is only part
   of the region's). If it is above 1, lower `gone_weight`. Judge hubs by market size *and* profit:
   thin hubs (Rens, Hek trade about 1/5 of Amarr's volume) fill slowly and tie capital up longer.
4. **Performance.** Compare net worth and realized P&L with the previous journal entry. Look at
   the worst items: are we losing to fees, to stale stock, or to bad picks? Is cash sitting idle
   while candidates go unused (raise sizing), or are we running out of slots or time?
5. **Experiments.** Compare the variants in the summary. If one has beaten main for about 2 weeks,
   promote its settings into the main config and start a new experiment (see STRATEGY.md open
   questions). Keep 2–3 variants.
   **Decide at most 1–2 changes** (`config.toml` parameters or code), each with a hypothesis
   and a way to tell whether it worked. Don't retune something before it has had about 3 days
   to show results.
6. **Speculation (Friday reviews only, at most 3 web searches).** Look for upcoming EVE changes:
   patch notes, dev blogs, and anything announced for the next 2–6 weeks. If a change clearly moves
   an item's price, add an entry to `state/spec.json` (format in STRATEGY.md) with the thesis in
   `note`. Spec stays at most 10% of net worth. Deactivate entries whose thesis has expired.
7. `python -m pytest -q`, commit with a clear message, push to the default branch.
8. Append a `JOURNAL.md` entry: date, numbers (net worth, % change, realized), what you
   changed, and why, plus what to check next time. Keep it under 15 lines.

Never edit the files under `state/` by hand, except `state/spec.json` or a deliberate reset that
the journal records. Open investigations live in STRATEGY.md's open questions; pick one up when
the pipeline is healthy and there's budget left.
