"""Post the long-form TEASERS (9:16, ~58s) to each brand's Instagram (Reel) and
TikTok (via Buffer). Every brand posts ONLY to its own accounts:
  - Instagram: META_PAGE_ID -> that Page's token -> its linked IG account.
  - TikTok: that brand's pinned Buffer channel id, double-checked against the
    channel NAME in Buffer before posting (skips the brand on any mismatch).
Idempotent via longform_social_state.json (keys "ig:<brand>" / "tt:<brand>").
Does not touch any daily-shorts schedule or state file.
"""
import os, json, time
import meta_common as M
import post_instagram as P
import buffer_tiktok as B

HERE = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(HERE, "longform_social_state.json")
TEASERS = os.path.join(HERE, "longform_teasers")
REPO = os.environ.get("GH_REPO", "MoazGamalMohamed/beyond-obvious")
SHA = os.environ.get("GITHUB_SHA", "claude/project-thread-sj3iu8")

def jsd(f): return "https://cdn.jsdelivr.net/gh/%s@%s/longform_teasers/%s" % (REPO, SHA, f)
def raw(f): return "https://raw.githubusercontent.com/%s/%s/longform_teasers/%s" % (REPO, SHA, f)

TAG = "\nOriginal animation · synthesized voices"
JOBS = [
 dict(key="bo", brand="Beyond Obvious", page="1413650968505167", file="BO_teaser.mp4",
      tt_id=os.environ.get("BO_TT_CHANNEL", "").strip(), tt_hint="beyond",
      hook="The shorter track LOST. \U0001f92f Two beads race for one bell, and the rematch gets even stranger. Which track would you bet on? \U0001f447",
      ig_tail="\n\nFull episode on our YouTube: youtu.be/CXvW9WUvXhk" + TAG +
              "\n#physics #brachistochrone #sciencefacts #didyouknow #stem #reels #learnsomething",
      tt_tail="\n\nFull episode on YouTube: Beyond Obvious" + TAG +
              "\n#physics #sciencetok #learnontiktok #didyouknow #stem #fyp",
      comment="Short track or long track? Drop your guess \U0001f447 Full episode is on our YouTube!"),
 dict(key="wl", brand="What If Lab", page="1484071088120232", file="WL_teaser.mp4",
      tt_id="6b061b9c8541f09ecb92ed0c", tt_hint="whatif",
      hook="Free toast if it lands butter-side down… what could go wrong? \U0001f35e Kiki takes the diner apart one bad assumption at a time. Which side hits the floor? \U0001f447",
      ig_tail="\n\nFull episode on our Facebook & YouTube: What If Lab" + TAG +
              "\n#physics #murphyslaw #butteredtoast #mythbusting #sciencefacts #reels",
      tt_tail="\n\nFull episode on Facebook & YouTube: What If Lab" + TAG +
              "\n#physics #mythbusting #sciencetok #learnontiktok #fyp",
      comment="Butter-side down or up? Place your bet \U0001f447 Full episode on our Facebook & YouTube!"),
 dict(key="iz", brand="Idiom Zoo", page="1494526067076336", file="IZ_teaser.mp4",
      tt_id="6b0780a98541f09ecba75af2", tt_hint="idiom",
      hook="The moon is missing, and Bruno has silver paint on his paws. \U0001f319\U0001f43e Would you accuse him? Call it before the reveal! \U0001f447",
      ig_tail="\n\nFull episode (+3 idioms to learn) on our YouTube: youtu.be/I8cH7lkTfNQ" + TAG +
              "\n#learnenglish #idioms #esl #englishlearning #animation #reels",
      tt_tail="\n\nFull episode on YouTube: Idiom Zoo" + TAG +
              "\n#learnenglish #idioms #esl #englishtok #learnontiktok #fyp",
      comment="Guilty or framed? Tell us your theory \U0001f447 Full episode is on our YouTube!"),
]

def save(state): json.dump(state, open(STATE, "w"), indent=1)

def do_instagram(j, state):
    k = "ig:" + j["key"]
    if k in state: M.log("IG skip (done):", j["brand"], state[k]); return
    os.environ["META_PAGE_ID"] = j["page"]
    pid, name, ptok, ig = M.resolve()
    if pid != j["page"] or not ig:
        M.log("IG SKIP %s: page %s ig %s" % (j["brand"], pid, ig)); return
    local = os.path.join(TEASERS, j["file"])
    mid = None
    for u in (jsd(j["file"]), raw(j["file"]), None):
        try:
            M.log("IG", name, "->", u or "(direct upload)")
            mid = P.publish_reel(ig, ptok, local, j["hook"] + j["ig_tail"], video_url=u)
            break
        except Exception as e:
            M.log("  IG attempt failed:", str(e)[:300])
    if not mid: M.log("IG FAILED:", j["brand"]); return
    state[k] = mid; save(state)
    M.log("  IG published", j["brand"], "media id", mid)
    try:
        M._req("%s/%s/comments" % (M.GRAPH, mid),
               data={"message": j["comment"], "access_token": ptok}, method="POST")
        M.log("  first comment posted")
    except Exception as e:
        M.log("  first comment skipped:", str(e)[:200])

def do_tiktok(j, state, key, tiktoks):
    k = "tt:" + j["key"]
    if k in state: M.log("TT skip (done):", j["brand"], state[k]); return
    cid = j["tt_id"]
    if not cid:  # BO channel id secret unset: find it by name (never auto-pick blindly)
        cand = [c for c in tiktoks if j["tt_hint"] in (c.get("name") or "").lower().replace(".", "").replace("_", "")]
        cid = cand[0]["id"] if len(cand) == 1 else ""
    ch = next((c for c in tiktoks if c["id"] == cid), None)
    nm = (ch or {}).get("name", "").lower().replace(".", "").replace("_", "")
    if not ch or j["tt_hint"] not in nm:
        M.log("TT SKIP %s: channel %s name %r does not match brand" % (j["brand"], cid, nm)); return
    text = j["hook"] + j["tt_tail"]
    for u in (raw(j["file"]), jsd(j["file"])):
        M.log("TT", j["brand"], "(%s) ->" % ch.get("name"), u)
        pid, err = B.create_post(key, cid, text, u, None)
        if pid:
            state[k] = pid; save(state); M.log("  TT handed to Buffer, post", pid); return
        M.log("  Buffer said:", err)
    M.log("TT FAILED:", j["brand"])

def main():
    state = M.load_json(STATE, {})
    for j in JOBS:
        if not os.path.exists(os.path.join(TEASERS, j["file"])):
            M.log("MISSING teaser:", j["file"]); continue
        do_instagram(j, state)
        time.sleep(2)
    key = os.environ.get("BUFFER_API_KEY", "").strip()
    if not key:
        M.log("No BUFFER_API_KEY - TikTok skipped.")
    else:
        tiktoks = [c for c in B.channels(key) if "tiktok" in (c.get("service") or "").lower()]
        M.log("Buffer TikTok channels:", [(c["id"], c.get("name")) for c in tiktoks])
        for j in JOBS:
            if os.path.exists(os.path.join(TEASERS, j["file"])):
                do_tiktok(j, state, key, tiktoks)
    M.log("Teasers done. state:", state)

if __name__ == "__main__":
    main()
