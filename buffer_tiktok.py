"""Fully hands-free TikTok posting through Buffer's API (free plan).

Why Buffer: TikTok only lets AUDITED apps publish publicly, and its audit needs
an on-screen consent composer that a headless studio cannot show. Buffer is
already an audited TikTok partner, and its API (included on the Free plan) can
publish a video from a public URL. So this job hands today's short to Buffer and
Buffer publishes it to TikTok - no TikTok developer app, no audit, no demo video.

Runs daily. Reads schedule.json, finds the item due in this posting slot and
creates a Buffer post (mode shareNow, automatic publishing) on the TikTok
channel. Idempotent via state_buffer.json.

Secrets:  BUFFER_API_KEY            (Buffer -> Settings -> API)
Optional: BUFFER_TIKTOK_CHANNEL_ID  (auto-discovered when unset)
Env:      MODE = post (default) | check   (check lists channels, posts nothing)

tiktok_auto.json holds {"start_publishAt": ISO}: items scheduled before it are
treated as already posted by hand and are never sent (prevents duplicates).
If BUFFER_API_KEY is not set the job exits quietly.
"""
import os
import sys
import json
import datetime
import urllib.request
import urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
SCHEDULE = os.path.join(HERE, "schedule.json")
STATE = os.path.join(HERE, "state_buffer.json")
CONFIG = os.path.join(HERE, "tiktok_auto.json")
API = "https://api.buffer.com"
REPO = os.environ.get("GH_REPO", "MoazGamalMohamed/beyond-obvious")
# Public, direct, stable video URLs (tried in order if Buffer rejects one).
BASES = [b for b in [
    os.environ.get("VIDEO_BASE_URL", "").strip(),
    "https://raw.githubusercontent.com/%s/main/videos/" % REPO,
    "https://cdn.jsdelivr.net/gh/%s@main/videos/" % REPO,
] if b]

BOOST = ("\n\nNew science short every day - follow Beyond Obvious."
         " #fyp #foryou #sciencetok #learnontiktok #stem")
DUE_WINDOW = datetime.timedelta(hours=18)


def log(*a):
    print(datetime.datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def gql(key, query, variables=None):
    """POST one GraphQL request. Returns (http_status, parsed_json)."""
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(API, data=body, method="POST", headers={
        "Authorization": "Bearer " + key, "Content-Type": "application/json",
        "User-Agent": "beyond-obvious-bot"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.getcode(), json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        txt = e.read().decode()[:800]
        try:
            return e.code, json.loads(txt)
        except ValueError:
            return e.code, {"_error": txt}


def gstr(s):
    """A GraphQL string literal (JSON escaping is valid GraphQL; keep UTF-8)."""
    return json.dumps(s, ensure_ascii=False)


def channels(key):
    st, j = gql(key, "query { account { organizations { id name } } }")
    orgs = (((j.get("data") or {}).get("account") or {}).get("organizations")) or []
    if not orgs:
        sys.exit("Buffer: could not read organizations (HTTP %s): %s" % (st, j))
    out = []
    for o in orgs:
        st, j = gql(key, "query($o: OrganizationId!) { channels(input: "
                         "{ organizationId: $o }) { id name service } }", {"o": o["id"]})
        out += ((j.get("data") or {}).get("channels")) or []
    return out


def tiktok_channel(key):
    cid = os.environ.get("BUFFER_TIKTOK_CHANNEL_ID", "").strip()
    if cid:
        return cid
    tt = [c for c in channels(key) if "tiktok" in (c.get("service") or "").lower()]
    if not tt:
        sys.exit("Buffer: no TikTok channel connected yet. Connect TikTok in Buffer first.")
    return tt[0]["id"]


def create_post(key, channel_id, text, video_url):
    q = ("mutation { createPost(input: { text: %s, channelId: %s, "
         "schedulingType: automatic, mode: shareNow, "
         "assets: [{ video: { url: %s, metadata: { thumbnailOffset: 1000 } } }] }) { "
         "... on PostActionSuccess { post { id } } "
         "... on MutationError { message } } }"
         % (gstr(text), gstr(channel_id), gstr(video_url)))
    st, j = gql(key, q)
    res = (j.get("data") or {}).get("createPost") or {}
    pid = (res.get("post") or {}).get("id")
    return pid, (res.get("message") or (None if pid else "HTTP %s: %s" % (st, j)))


def load(path, default):
    return json.load(open(path)) if os.path.exists(path) else default


def iso(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def due_item(sched, state, start):
    now = datetime.datetime.now(datetime.timezone.utc)
    best = None
    for it in sched["items"]:
        pub = iso(it["publishAt"])
        if it["video_file"] in state["posted"] or pub < start:
            continue
        if pub <= now and (now - pub) <= DUE_WINDOW:
            if best is None or pub > best[0]:
                best = (pub, it)
    return best[1] if best else None


def main():
    key = os.environ.get("BUFFER_API_KEY", "").strip()
    if not key:
        log("Buffer not configured yet (no BUFFER_API_KEY) - skipping."); return
    mode = (os.environ.get("MODE") or "post").strip()
    cfg = load(CONFIG, {})
    start = iso(cfg.get("start_publishAt", "2026-12-16T12:00:00Z"))

    if mode == "check":
        chs = channels(key)
        for c in chs:
            log("channel:", c.get("service"), "|", c.get("name"))
        tt = [c for c in chs if "tiktok" in (c.get("service") or "").lower()]
        log("TikTok connected:", "YES" if tt else "NO - connect TikTok in Buffer")
        log("auto-posting starts with items scheduled at/after", start.isoformat())
        sched = load(SCHEDULE, {"items": []})
        nxt = sorted(i["publishAt"] for i in sched["items"] if iso(i["publishAt"]) >= start)
        log("next item to auto-post:", nxt[0] if nxt else "none queued yet")
        return

    if mode == "validate":
        # Schema check with no side effects: a channel id that is not ours can
        # never publish. "Channel not found"-style reply = request shape is valid;
        # a GraphQL "errors" reply = the shape needs fixing.
        pid, err = create_post(key, "000000000000000000000000", "validation only",
                               BASES[0] + "02_Thu-Nov26_BO-001.mp4")
        log("validate:", "UNEXPECTED post %s" % pid if pid else err)
        return

    sched = load(SCHEDULE, {"items": []})
    state = load(STATE, {"posted": {}})
    it = due_item(sched, state, start)
    if not it:
        log("No TikTok item due in this slot."); return
    cid = tiktok_channel(key)
    text = it["caption"] + BOOST
    pid, err = None, None
    for base in BASES:
        url = base + it["video_file"]
        log("posting via Buffer:", it["episode"], "|", url)
        pid, err = create_post(key, cid, text, url)
        if pid:
            break
        log("  Buffer said:", err)
    if not pid:
        sys.exit("Buffer post failed: %s" % err)
    state["posted"][it["video_file"]] = {"buffer_post_id": pid, "episode": it["episode"]}
    json.dump(state, open(STATE, "w"), indent=1)
    log("  done - Buffer post", pid, "is publishing to TikTok.")


if __name__ == "__main__":
    main()
