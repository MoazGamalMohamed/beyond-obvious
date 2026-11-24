"""Send the Beyond Obvious short that's due today to TikTok (inbox-upload flow).

Runs daily (like Instagram). Reads schedule.json, finds the item due in this
posting slot, and uploads the video to the authorizing account's TikTok INBOX
via the Content Posting API (Upload, FILE_UPLOAD). You then get a TikTok
notification, open it, add the caption, and tap Post — the final publish happens
inside TikTok's own app. Idempotent via state_tiktok.json.

Why inbox-upload (video.upload) and not Direct Post (video.publish):
TikTok's Direct Post audit requires the app to show an on-screen consent/preview
composer before publishing. This studio is headless (a daily cron, no UI), so it
cannot show that screen. The inbox-upload flow instead hands the final
caption/privacy/publish step to TikTok's own app, which is a flow a headless
sender is allowed to use once the app is approved for the video.upload scope.

The caption is NOT sent by the API in this flow (TikTok has you write it in-app).
The job logs the suggested caption so you can copy it; the same text ships in the
weekly caption pack.

If no TikTok secrets are configured yet, the job exits quietly (no error), so it
is safe to have this workflow present before you finish the setup.
"""
import os
import sys
import json
import time
import datetime
import tiktok_common as T

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEDULE = os.path.join(HERE, "schedule.json")
STATE = os.path.join(HERE, "state_tiktok.json")
VIDEOS = os.path.join(HERE, "videos")
OPEN = T.OPEN

# Suggested caption (you paste/confirm it in the TikTok app before posting).
BOOST = ("\n\nNew science short every day - follow Beyond Obvious."
         " #fyp #foryou #sciencetok #learnontiktok #stem")

# Only send an item whose 6 PM slot has arrived within this window, so the first
# run after setup sends just today's short, not a backlog of past days.
DUE_WINDOW = datetime.timedelta(hours=18)


def iso(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def due_item(sched, state):
    now = datetime.datetime.now(datetime.timezone.utc)
    best = None
    for it in sched["items"]:
        if it["video_file"] in state["posted"]:
            continue
        pub = iso(it["publishAt"])
        if pub <= now and (now - pub) <= DUE_WINDOW:
            if best is None or pub > best[0]:
                best = (pub, it)
    return best[1] if best else None


def upload_to_inbox(tok, vpath):
    """Upload one video to the user's TikTok inbox. Returns (publish_id, status).

    Inbox-upload init takes only source_info - no title/caption/privacy. The
    creator completes those in the TikTok app. Terminal success for this flow is
    SEND_TO_USER_INBOX (the video is waiting in the account's notifications).
    """
    size = os.path.getsize(vpath)
    body = {
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": size,
            "chunk_size": size,          # single chunk (our files are < 64 MB)
            "total_chunk_count": 1,
        },
    }
    code, j = T._req(OPEN + "/v2/post/publish/inbox/video/init/",
                     raw=json.dumps(body).encode(),
                     headers={"Authorization": "Bearer " + tok,
                              "Content-Type": "application/json"}, method="POST")
    data = j.get("data", {})
    pid, url = data.get("publish_id"), data.get("upload_url")
    if not url:
        sys.exit("inbox init failed (HTTP %s): %s" % (code, j))
    with open(vpath, "rb") as f:
        raw = f.read()
    code, _ = T._req(url, raw=raw, method="PUT",
                     headers={"Content-Type": "video/mp4",
                              "Content-Length": str(size),
                              "Content-Range": "bytes 0-%d/%d" % (size - 1, size)})
    T.log("  upload HTTP", code)
    for _ in range(40):
        time.sleep(5)
        code, s = T._req(OPEN + "/v2/post/publish/status/fetch/",
                         raw=json.dumps({"publish_id": pid}).encode(),
                         headers={"Authorization": "Bearer " + tok,
                                  "Content-Type": "application/json"}, method="POST")
        st = s.get("data", {}).get("status")
        if st in ("SEND_TO_USER_INBOX", "PUBLISH_COMPLETE"):
            return pid, st
        if st == "FAILED":
            sys.exit("inbox send FAILED: %s" % s)
    return pid, "PENDING"


def main():
    if not os.environ.get("TIKTOK_REFRESH_TOKEN"):
        T.log("TikTok not configured yet (no TIKTOK_REFRESH_TOKEN) - skipping.")
        return
    tok, open_id = T.refresh_access_token()
    sched = T.load_json(SCHEDULE, {"items": []})
    state = T.load_json(STATE, {"posted": {}})
    it = due_item(sched, state)
    if not it:
        T.log("No TikTok item due in this slot."); return

    vpath = os.path.join(VIDEOS, it["video_file"])
    if not os.path.exists(vpath):
        sys.exit("MISSING: %s" % vpath)
    T.log("sending to TikTok inbox:", it["episode"], "|", it.get("local_time_note", ""))
    T.log("  suggested caption:", (it["caption"] + BOOST).replace("\n", " "))
    pid, st = upload_to_inbox(tok, vpath)
    state["posted"][it["video_file"]] = {"publish_id": pid, "status": st}
    T.save_json(STATE, state)
    T.log("  done:", pid, st, "- open the TikTok notification to finish the post.")


if __name__ == "__main__":
    main()
