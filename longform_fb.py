"""Publish the three long-form brand videos to each brand's Facebook Page as a
full Page VIDEO (not a Reel — Reels cap at 90s; these are 5-10 min).

One secret: META_TOKEN (same user/page token the reel jobs use). For each brand
we set META_PAGE_ID and let meta_common.resolve() hand back that Page's own
token, so a video is never posted to the wrong Page. Idempotent via
longform_fb_state.json so re-runs never double-post.
"""
import os, json, time
import requests
import meta_common as M

HERE = os.path.dirname(os.path.abspath(__file__))
VIDEOS = os.path.join(HERE, "longform")
STATE = os.path.join(HERE, "longform_fb_state.json")
GVIDEO = "https://graph-video.facebook.com/" + M.GV

JOBS = [
 {"brand":"Beyond Obvious", "page":"1413650968505167",
  "file":"Beyond_Obvious_The_Longer_Track.mp4",
  "title":"The Longer Track Won. Then We Moved the Starting Line.",
  "desc":("Two beads race for one bell. The shorter path loses - then the rematch gets "
          "stranger. We animated the beads straight from the equations of motion and "
          "checked the clock with an independent calculation. Can you call which track "
          "wins before the bell?\n\n"
          "Original 3D animation and calculations by Beyond Obvious. Noodle and Pip are "
          "fictional characters with synthesized stock-style voices.\n\n"
          "#physics #brachistochrone #sciencefacts #didyouknow #animation #stem #learnsomething")},
 {"brand":"What If Lab", "page":"1484071088120232",
  "file":"What_If_Lab_The_Toast_Guarantee.mp4",
  "title":"He Offered Free Toast If It Landed Butter-Side Down",
  "desc":("Bruno's diner gives you free toast if a slice lands butter-side down. His first "
          "customer has friends. Kiki takes the place apart one bad assumption at a time - "
          "can you call which side lands before the floor moves?\n\n"
          "An original What If Lab cartoon with an identified physics simulation. Fictional "
          "characters with synthesized voices.\n\n"
          "#physics #murphyslaw #butteredtoast #mythbusting #sciencefacts #animation #stem")},
 {"brand":"Idiom Zoo", "page":"1494526067076336",
  "file":"Idiom_Zoo_Who_Stole_the_Moon (1).mp4",
  "title":"Who Stole the Moon? | The Silver Pawprint Mystery",
  "desc":("The curtain is up in five minutes, the moon is missing, and Bruno has silver "
          "paint on his paws. Would you accuse him? A sung backstage mystery that sneaks in "
          "three English idioms - steal the show, in the spotlight, jump to conclusions. "
          "Pick your explanation before the camera goes around the side!\n\n"
          "An original Idiom Zoo story. Kiki, Bruno and Mabel are fictional characters with "
          "synthesized voices.\n\n"
          "#learnenglish #idioms #esl #englishlearning #animation #storytime")},
]

def main():
    state = M.load_json(STATE, {"posted": {}})
    for j in JOBS:
        if j["file"] in state["posted"]:
            M.log("skip (already on FB):", j["brand"], state["posted"][j["file"]]); continue
        os.environ["META_PAGE_ID"] = j["page"]
        pid, name, ptok, _ig = M.resolve()
        if pid != j["page"]:
            M.log("SKIP page mismatch:", pid, "!=", j["page"]); continue
        vpath = os.path.join(VIDEOS, j["file"])
        if not os.path.exists(vpath):
            M.log("MISSING video:", vpath); continue
        M.log("FB upload:", name, pid, "|", j["file"], "%.1fMB" % (os.path.getsize(vpath)/1e6))
        with open(vpath, "rb") as f:
            r = requests.post("%s/%s/videos" % (GVIDEO, pid),
                              data={"access_token": ptok, "title": j["title"],
                                    "description": j["desc"], "published": "true"},
                              files={"source": (j["file"], f, "video/mp4")}, timeout=1200)
        if r.status_code >= 400:
            M.log("  ERROR %s: %s" % (r.status_code, r.text[:400])); continue
        vid = r.json().get("id")
        state["posted"][j["file"]] = vid; M.save_json(STATE, state)
        M.log("  posted id=%s -> https://www.facebook.com/%s/videos/%s" % (vid, pid, vid))
        time.sleep(2)
    M.log("Facebook long-form done.")

if __name__ == "__main__":
    main()
