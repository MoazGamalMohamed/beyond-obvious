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
SCHEDULE = os.path.join(HERE, "schedule.json")
STATE = os.path.join(HERE, "state_ig.json")
VIDEOS = os.path.join(HERE, "videos")

# Reach booster appended to every caption (CTA + extra discovery hashtags).
BOOST = ("\n\nNew science short every day — follow @beyondobvious for your daily "
         "dose of \"wait, really?\"\n"
         "#sciencefacts #didyouknow #stem #funfacts #educational #sciencetok #learnsomething")
# Author's first comment, posted right after publish (extra reach; needs
# instagram_manage_comments — skipped automatically if not granted).
FIRST_COMMENT = "Which one surprised you? \U0001f447 Follow for a new science short every day!"


def publish_reel(ig_id, tok, video_path, caption):
    # 1) create a resumable Reels container
    j = M._req("%s/%s/media" % (M.GRAPH, ig_id),
               data={"media_type": "REELS", "upload_type": "resumable",
                     "caption": caption, "access_token": tok}, method="POST")
    cid = j["id"]
    # 2) upload the local file to the IG upload endpoint
    size = os.path.getsize(video_path)
    with open(video_path, "rb") as f:
        M._req("%s/%s" % (M.RUPLOAD_IG, cid),
               headers={"Authorization": "OAuth " + tok, "offset": "0",
                        "file_size": str(size)}, raw=f.read(), method="POST")
    # 3) poll until the container is FINISHED (<=5 min)
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
    state = M.load_json(STATE, {"posted": {}})
    today = M.today_chicago()
    due = None
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
    M.log("publishing IG reel:", due["episode"], due["local_time_note"])
    mid = publish_reel(ig_id, tok, vpath, due["caption"] + BOOST)
    state["posted"][due["video_file"]] = mid
    M.save_json(STATE, state)
    M.log("  published id=", mid)
    # reach booster: author's first comment (best-effort)
    try:
        M._req("%s/%s/comments" % (M.GRAPH, mid),
               data={"message": FIRST_COMMENT, "access_token": tok}, method="POST")
        M.log("  first comment posted")
    except Exception as e:
        M.log("  first comment skipped:", e)


if __name__ == "__main__":
    main()
