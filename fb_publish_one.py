"""Publish ONE Facebook reel immediately (fix a stuck/failed scheduled reel).

Optionally deletes a stale video id first (the stuck scheduled reel), then
re-uploads the local video and publishes it now. Updates the FB state file so
the new id replaces the old one. Only touches the single VIDEO_FILE given.
"""
import os
import json
import meta_common as M
import post_facebook as F

HERE = os.path.dirname(os.path.abspath(__file__))
VF = os.environ["VIDEO_FILE"]
SCHEDULE = os.path.join(HERE, os.environ.get("SCHEDULE_FILE", "schedule.json"))
STATE = os.path.join(HERE, os.environ.get("STATE_FILE", "state_fb.json"))
VIDEOS = os.path.join(HERE, os.environ.get("VIDEOS_DIR", "videos"))
DEL = os.environ.get("DELETE_VIDEO_ID", "").strip()


def main():
    pid, name, tok, _ = M.resolve()
    M.log("Page:", name, pid)
    if DEL:
        try:
            r = M._req("%s/%s?access_token=%s" % (M.GRAPH, DEL, tok), method="DELETE")
            M.log("deleted stale reel", DEL, r)
        except Exception as e:
            M.log("delete failed (continuing):", e)
    sched = json.load(open(SCHEDULE))
    boost = sched.get("_boost", F.DEFAULT_BOOST)
    it = next((i for i in sched.get("items", []) if i["video_file"] == VF), None)
    if not it:
        raise SystemExit("video_file not in schedule: " + VF)
    vpath = os.path.join(VIDEOS, VF)
    if not os.path.exists(vpath):
        raise SystemExit("missing video: " + vpath)
    M.log("publishing NOW:", it.get("episode"), VF)
    vid = F.post_reel(pid, tok, vpath, it["caption"] + boost, 0, publish_now=True)
    state = json.load(open(STATE)) if os.path.exists(STATE) else {"posted": {}}
    state["posted"][VF] = vid
    json.dump(state, open(STATE, "w"), indent=1)
    M.log("published id=", vid)


if __name__ == "__main__":
    main()
