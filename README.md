# Beyond Obvious — Instagram + Facebook auto-poster

Free, hands-free posting to Instagram Reels and Facebook Reels, run by GitHub
Actions (no server, no PC needed).

## How it works
- **Facebook** (`post_facebook.py`, weekly): uploads the week's Reels and
  schedules each to go public at 6 PM Central on its day. Facebook handles the
  daily go-live.
- **Instagram** (`post_instagram.py`, daily at 00:00 UTC = 6 PM Central):
  Instagram's API can't pre-schedule, so this runs each day and publishes that
  day's Reel.
- `schedule.json` — the week's videos, captions, and go-live times.
- `videos/` — the Reel files for the current week.
- `state_fb.json` / `state_ig.json` — remember what's posted so nothing doubles.

## The only secret
One repository secret, `META_TOKEN` = a long-lived Facebook **Page** access
token. The scripts resolve the Page id and the linked Instagram account from it.
Set it under **Settings → Secrets and variables → Actions → New repository secret**.

## Each week
Claude replaces `schedule.json` and the files in `videos/` with the new week's
batch; the two schedules then run on their own.

Everything here is free: GitHub Actions' free minutes and Meta's Graph API.
