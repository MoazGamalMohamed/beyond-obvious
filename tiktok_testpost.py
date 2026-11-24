"""One-off: send a single chosen video to the TikTok inbox right now.

Used once to (a) verify the integration end-to-end and (b) produce the footage
for the app-review demo. Independent of schedule.json / the daily due-window, so
it works even before the first scheduled post. Reuses the exact production
upload path (tiktok_post.upload_to_inbox) so the test proves the real code.

Env: FILE (video filename under videos/, optional; defaults to the first short)
plus the usual TIKTOK_CLIENT_KEY / TIKTOK_CLIENT_SECRET / TIKTOK_REFRESH_TOKEN
(and GH_PAT/GH_REPO so a rotated refresh token is persisted).
"""
import os
import sys
import tiktok_common as T
import tiktok_post as P

DEFAULT_FILE = "02_Thu-Nov26_BO-001.mp4"


def main():
    if not os.environ.get("TIKTOK_REFRESH_TOKEN"):
        sys.exit("No TIKTOK_REFRESH_TOKEN set - finish the one-time OAuth first.")
    fname = os.environ.get("FILE", "").strip() or DEFAULT_FILE
    vpath = os.path.join(P.VIDEOS, fname)
    if not os.path.exists(vpath):
        sys.exit("MISSING: %s" % vpath)
    tok, _ = T.refresh_access_token()
    T.log("TEST: sending to TikTok inbox:", fname)
    pid, st = P.upload_to_inbox(tok, vpath)
    T.log("  done:", pid, st)
    T.log("  Open the TikTok app -> Inbox/Notifications to finish and post it.")


if __name__ == "__main__":
    main()
