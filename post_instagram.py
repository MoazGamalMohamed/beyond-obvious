"""Post today's Instagram Reel (runs daily; IG's API can't pre-schedule).

Picks the schedule item whose local (Chicago) date is today and publishes it.
Idempotent via state_ig.json.
"""
import os
import sys
import time
import datetime
import meta_common as M

HERE = os.path.dirname(os.path.abspath(__file__))
# Per-brand overrides (default = Beyond Obvious, so existing runs are unchanged).
SCHEDULE = os.path.join(HERE, os.environ.get("SCHEDULE_FILE", "schedule.json"))
STATE = os.path.join(HERE, os.environ.get("STATE_FILE", "state_ig.json"))
VIDEOS = os.path.join(HERE, os.environ.get("VIDEOS_DIR", "videos"))
# Optional public base URL. When set, Instagram fetches the video from
# VIDEO_BASE_URL/<video_file> (reliable) instead of a resumable byte upload.
VIDEO_BASE_URL = os.environ.get("VIDEO_BASE_URL", "").rstrip("/")

# Reach booster appended to every caption (CTA + extra discovery hashtags).
# A schedule file may override these with top-level "_boost" / "_first_comment".
DEFAULT_BOOST = ("\n\nNew science short every day — follow @beyondobvious for your daily "
                 "dose of \"wait, really?\"\n"
                 "#sciencefacts #didyouknow #stem #funfacts #educational #sciencetok #learnsomething")
# Author's first comment, posted right after publish (extra reach; needs
# instagram_manage_comments — skipped automatically if not granted).
DEFAULT_FIRST_COMMENT = "Which one surprised you? \U0001f447 Follow for a new science short every day!"


def _with_thumb(data, thumb_offset):
    """Reel cover = the frame at thumb_offset ms (schedule item `thumb_offset_ms`).
    Without it Instagram uses frame 0, which for older renders is a blank intro card."""
    if thumb_offset:
        data["thumb_offset"] = str(int(thumb_offset))
    return data


def publish_reel(ig_id, tok, video_path, caption, video_url=None, thumb_offset=None):
    # 1) create the Reels container
    if video_url:
        # Preferred: Instagram fetches the file from a public URL (served as
        # video/mp4). Far more reliable than the resumable byte upload, which
        # returns ProcessingFailedError for some files.
        j = M._req("%s/%s/media" % (M.GRAPH, ig_id),
                   data=_with_thumb({"media_type": "REELS", "video_url": video_url,
                         "caption": caption, "access_token": tok}, thumb_offset), method="POST")
        cid = j["id"]
    else:
        # Fallback: resumable binary upload of the local file.
        j = M._req("%s/%s/media" % (M.GRAPH, ig_id),
                   data=_with_thumb({"media_type": "REELS", "upload_type": "resumable",
                         "caption": caption, "access_token": tok}, thumb_offset), method="POST")
        cid = j["id"]
        size = os.path.getsize(video_path)
        with open(video_path, "rb") as f:
            M._req("%s/%s" % (M.RUPLOAD_IG, cid),
                   headers={"Authorization": "OAuth " + tok, "offset": "0",
                            "file_size": str(size)}, raw=f.read(), method="POST")
    # 2) poll until the container is FINISHED (<=5 min)
    for _ in range(30):
        st = M.get("%s" % cid, tok=tok, fields="status_code")
        code = st.get("status_code")
        if code == "FINISHED":
            break
        if code == "ERROR":
            raise RuntimeError("container error: %s" % st)
        time.sleep(10)
    else:
        raise RuntimeError("container not ready after 5 min")
    # 4) publish
    r = M._req("%s/%s/media_publish" % (M.GRAPH, ig_id),
               data={"creation_id": cid, "access_token": tok}, method="POST")
    return r["id"]


def main():
    page_id, name, tok, ig_id = M.resolve()
    if not ig_id:
        sys.exit("No Instagram business account is linked to this Page. "
                 "Link the IG (Creator) account to the Page and retry.")
    M.log("Instagram account:", ig_id, "(Page:", name + ")")
    sched = M.load_json(SCHEDULE, {"items": []})
    boost = sched.get("_boost", DEFAULT_BOOST)
    first_comment = sched.get("_first_comment", DEFAULT_FIRST_COMMENT)
    state = M.load_json(STATE, {"posted": {}})
    today = M.today_chicago()
    # CATCHUP=1: self-heal a slot whose run failed by posting the OLDEST not-yet-
    # posted item whose local date is today or within the last MAX_CATCHUP_DAYS
    # days (so a wiped state file can't dump very old content). Default off, so
    # Beyond Obvious / Idiom Zoo keep their exact today-only behavior.
    catchup = os.environ.get("CATCHUP", "") == "1"
    max_back = int(os.environ.get("MAX_CATCHUP_DAYS", "7"))
    due = None
    if catchup:
        cands = []
        for it in sched["items"]:
            d = datetime.datetime.strptime(it["publishAt"], "%Y-%m-%dT%H:%M:%SZ")
            local_date = (d - datetime.timedelta(hours=6)).date()  # UTC->Chicago
            if it["video_file"] in state["posted"]:
                continue
            if (today - datetime.timedelta(days=max_back)) <= local_date <= today:
                cands.append((local_date, it))
        if cands:
            cands.sort(key=lambda x: x[0])
            due = cands[0][1]
    else:
        for it in sched["items"]:
            d = datetime.datetime.strptime(it["publishAt"], "%Y-%m-%dT%H:%M:%SZ")
            local_date = (d - datetime.timedelta(hours=6)).date()  # UTC->Chicago
            if local_date == today and it["video_file"] not in state["posted"]:
                due = it; break
    if not due:
        M.log("Nothing due today (", today, ") or already posted."); return
    vpath = os.path.join(VIDEOS, due["video_file"])
    if not os.path.exists(vpath):
        sys.exit("MISSING video: %s" % vpath)
    vurl = (VIDEO_BASE_URL + "/" + due["video_file"]) if VIDEO_BASE_URL else None
    M.log("publishing IG reel:", due["episode"], due.get("local_time_note", ""),
          "(via hosted URL)" if vurl else "(via upload)")
    mid = publish_reel(ig_id, tok, vpath, due["caption"] + boost, video_url=vurl,
                       thumb_offset=due.get("thumb_offset_ms"))
    state["posted"][due["video_file"]] = mid
    M.save_json(STATE, state)
    M.log("  published id=", mid)
    # reach booster: author's first comment (best-effort)
    try:
        M._req("%s/%s/comments" % (M.GRAPH, mid),
               data={"message": first_comment, "access_token": tok}, method="POST")
        M.log("  first comment posted")
    except Exception as e:
        M.log("  first comment skipped:", e)


if __name__ == "__main__":
    main()
