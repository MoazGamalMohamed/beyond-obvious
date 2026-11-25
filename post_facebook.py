"""Schedule the week's Facebook Reels (runs weekly; FB publishes them daily).

Each Reel is uploaded once and set to go public at its scheduled time, so this
job only runs once per week. Idempotent via state_fb.json.
"""
import os
import sys
import datetime
import urllib.request
import meta_common as M

HERE = os.path.dirname(os.path.abspath(__file__))
# Per-brand overrides (default = Beyond Obvious, so existing runs are unchanged).
SCHEDULE = os.path.join(HERE, os.environ.get("SCHEDULE_FILE", "schedule.json"))
STATE = os.path.join(HERE, os.environ.get("STATE_FILE", "state_fb.json"))
VIDEOS = os.path.join(HERE, os.environ.get("VIDEOS_DIR", "videos"))

# Reach booster appended to every NEW reel description (CTA + discovery hashtags).
# Reels already in the state file keep their original caption. A schedule file may
# override it with a top-level "_boost" string (e.g. a second brand).
DEFAULT_BOOST = ("\n\nNew science short every day — follow Beyond Obvious for your daily "
                 "dose of \"wait, really?\"\n"
                 "#sciencefacts #didyouknow #stem #funfacts #educational #reels #learnsomething")


def post_reel(page_id, tok, video_path, description, publish_unix):
    # 1) start
    j = M._req("%s/%s/video_reels" % (M.GRAPH, page_id),
               data={"upload_phase": "start", "access_token": tok})
    vid = j["video_id"]
    # 2) upload bytes
    size = os.path.getsize(video_path)
    with open(video_path, "rb") as f:
        M._req("%s/%s" % (M.RUPLOAD_FB, vid),
               headers={"Authorization": "OAuth " + tok, "offset": "0",
                        "file_size": str(size), "Content-Type": "application/octet-stream"},
               raw=f.read(), method="POST")
    # 3) finish -> schedule
    M._req("%s/%s/video_reels" % (M.GRAPH, page_id),
           data={"access_token": tok, "video_id": vid, "upload_phase": "finish",
                 "video_state": "SCHEDULED", "scheduled_publish_time": str(publish_unix),
                 "description": description, "is_ai_generated": "true"}, method="POST")
    return vid


def main():
    page_id, name, tok, _ = M.resolve()
    M.log("Facebook Page:", name, page_id)
    sched = M.load_json(SCHEDULE, {"items": []})
    boost = sched.get("_boost", DEFAULT_BOOST)
    state = M.load_json(STATE, {"posted": {}})
    now = datetime.datetime.now(datetime.timezone.utc)
    for it in sched["items"]:
        key = it["video_file"]
        if key in state["posted"]:
            M.log("skip (done):", key); continue
        pub = M.to_unix(it["publishAt"])
        when = datetime.datetime.fromtimestamp(pub, datetime.timezone.utc)
        if when < now + datetime.timedelta(minutes=20):
            M.log("skip (go-live too soon/past):", key); continue
        vpath = os.path.join(VIDEOS, key)
        if not os.path.exists(vpath):
            M.log("MISSING:", vpath); continue
        M.log("scheduling FB reel:", it["episode"], it.get("local_time_note", ""))
        vid = post_reel(page_id, tok, vpath, it["caption"] + boost, pub)
        state["posted"][key] = vid
        M.save_json(STATE, state)
        M.log("  scheduled id=", vid)
    M.log("Facebook done.")


if __name__ == "__main__":
    main()
