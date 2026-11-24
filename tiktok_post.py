"""Post the Beyond Obvious short that's due today to TikTok.

Runs daily (like Instagram). Reads schedule.json, finds the item due in this
posting slot, uploads the video to TikTok via the Content Posting API
(Direct Post, FILE_UPLOAD), and publishes it. Idempotent via state_tiktok.json.

Audit gate: TikTok restricts UNAUDITED apps to SELF_ONLY (private) posts. The
script asks TikTok which privacy levels the app is allowed to use and honours
that. Once the app passes TikTok's audit, set the secret
TIKTOK_PRIVACY=PUBLIC_TO_EVERYONE and it posts publicly, fully hands-free.

If no TikTok secrets are configured yet, the job exits quietly (no error), so it
is safe to merge before you finish the setup.
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

# Reach booster + TikTok discovery tags appended to every caption (title field).
BOOST = ("\n\nNew science short every day — follow Beyond Obvious."
         " #fyp #foryou #sciencetok #learnontiktok #stem")

# Only post an item whose 6 PM slot has arrived within this window, so a first
# run after setup posts just today's short, not a backlog of past days.
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


def creator_info(tok):
    code, j = T._req(OPEN + "/v2/post/publish/creator_info/query/", raw=b"{}",
                     headers={"Authorization": "Bearer " + tok,
                              "Content-Type": "application/json"}, method="POST")
    return j.get("data", {})


def publish(tok, vpath, caption, privacy):
    size = os.path.getsize(vpath)
    body = {
        "post_info": {
            "title": caption[:2200],
            "privacy_level": privacy,
            "disable_comment": False,
            "disable_duet": False,
            "disable_stitch": False,
            "video_cover_timestamp_ms": 1000,
        },
        "source_info": {
            "source": "FILE_UPLOAD",
            "video_size": size,
            "chunk_size": size,          # single chunk (our files are ~3-5 MB)
            "total_chunk_count": 1,
        },
    }
    code, j = T._req(OPEN + "/v2/post/publish/video/init/",
                     raw=json.dumps(body).encode(),
                     headers={"Authorization": "Bearer " + tok,
                              "Content-Type": "application/json"}, method="POST")
    data = j.get("data", {})
    pid, url = data.get("publish_id"), data.get("upload_url")
    if not url:
        sys.exit("init failed (HTTP %s): %s" % (code, j))
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
        if st in ("PUBLISH_COMPLETE", "SEND_TO_USER_INBOX"):
            return pid, st
        if st == "FAILED":
            sys.exit("publish FAILED: %s" % s)
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

    privacy = os.environ.get("TIKTOK_PRIVACY", "SELF_ONLY")
    info = creator_info(tok)
    allowed = info.get("privacy_level_options", [])
    if allowed and privacy not in allowed:
        T.log("privacy %s not permitted yet (allowed: %s) - using %s" % (privacy, allowed, allowed[0]))
        privacy = allowed[0]

    vpath = os.path.join(VIDEOS, it["video_file"])
    if not os.path.exists(vpath):
        sys.exit("MISSING: %s" % vpath)
    T.log("posting to TikTok:", it["episode"], "|", it.get("local_time_note", ""), "| privacy=", privacy)
    pid, st = publish(tok, vpath, it["caption"] + BOOST, privacy)
    state["posted"][it["video_file"]] = {"publish_id": pid, "status": st, "privacy": privacy}
    T.save_json(STATE, state)
    T.log("  done:", pid, st)


if __name__ == "__main__":
    main()
