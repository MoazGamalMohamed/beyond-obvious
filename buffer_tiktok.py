"""Fully hands-free TikTok posting through Buffer's API (free plan).

Why Buffer: TikTok only lets AUDITED apps publish publicly, and its audit needs
an on-screen consent composer that a headless studio cannot show. Buffer is
already an audited TikTok partner, and its API (included on the Free plan) can
publish a video from a public URL. So this job hands today's short to Buffer and
Buffer publishes it to TikTok - no TikTok developer app, no audit, no demo video.

Runs daily. Reads schedule.json and PRE-SCHEDULES every upcoming item inside
Buffer (mode customScheduled, dueAt = the 6 PM slot, automatic publishing), up to
the Free-plan queue size; Buffer then publishes on time by itself. A slot that
has just passed unscheduled is published immediately. Idempotent via
state_buffer.json.

Secrets:  BUFFER_API_KEY            (Buffer -> Settings -> API)
Optional: BUFFER_TIKTOK_CHANNEL_ID  (auto-discovered when unset)
Env:      MODE = post (default) | check | validate   (the last two post nothing)

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
# Per-brand overrides (default = Beyond Obvious, so existing runs are unchanged).
SCHEDULE = os.path.join(HERE, os.environ.get("SCHEDULE_FILE", "schedule.json"))
STATE = os.path.join(HERE, os.environ.get("STATE_FILE", "state_buffer.json"))
CONFIG = os.path.join(HERE, os.environ.get("CONFIG_FILE", "tiktok_auto.json"))
API = "https://api.buffer.com"
REPO = os.environ.get("GH_REPO", "MoazGamalMohamed/beyond-obvious")
# Public, direct, stable video URLs (tried in order if Buffer rejects one).
BASES = [b for b in [
    os.environ.get("VIDEO_BASE_URL", "").strip(),
    "https://raw.githubusercontent.com/%s/main/videos/" % REPO,
    "https://cdn.jsdelivr.net/gh/%s@main/videos/" % REPO,
] if b]

DEFAULT_BOOST = ("\n\nNew science short every day - follow Beyond Obvious."
                 " #fyp #foryou #sciencetok #learnontiktok #stem")
DUE_WINDOW = datetime.timedelta(hours=18)
MAX_QUEUE = 9          # Buffer Free keeps at most 10 scheduled posts per channel


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
        out += [dict(c, org=o["id"]) for c in (((j.get("data") or {}).get("channels")) or [])]
    return out


def queued_posts(key, org_id, channel_id):
    """Posts Buffer currently holds for the channel: [(dueAt, status, id)]."""
    q = ("query { posts(first: 50, input: { organizationId: %s, filter: { channelIds: [%s] }, "
         "sort: [{ field: dueAt, direction: asc }] }) { edges { node { id status dueAt } } } }"
         % (gstr(org_id), gstr(channel_id)))
    st, j = gql(key, q)
    edges = (((j.get("data") or {}).get("posts")) or {}).get("edges")
    if edges is None:
        log("could not list posts (HTTP %s): %s" % (st, str(j)[:400])); return []
    return [(e["node"].get("dueAt"), e["node"].get("status"), e["node"].get("id")) for e in edges]


def tiktok_channel(key):
    cid = os.environ.get("BUFFER_TIKTOK_CHANNEL_ID", "").strip()
    if cid:
        return cid
    # A second brand MUST pin its own channel id, or we could post it to the first
    # (Beyond Obvious) TikTok channel. REQUIRE_CHANNEL_ID=1 forbids auto-discovery.
    if os.environ.get("REQUIRE_CHANNEL_ID", "").strip() in ("1", "true", "yes"):
        sys.exit("Buffer: BUFFER_TIKTOK_CHANNEL_ID is required for this brand but not set "
                 "(refusing to auto-pick a channel). Connect this brand's TikTok in Buffer "
                 "and set its channel id.")
    tt = [c for c in channels(key) if "tiktok" in (c.get("service") or "").lower()]
    if not tt:
        sys.exit("Buffer: no TikTok channel connected yet. Connect TikTok in Buffer first.")
    return tt[0]["id"]


def create_post(key, channel_id, text, video_url, due_at=None):
    """due_at=None publishes now; otherwise Buffer holds it until due_at (UTC ISO)."""
    when = ("mode: customScheduled, dueAt: %s" % gstr(due_at)) if due_at else "mode: shareNow"
    q = ("mutation { createPost(input: { text: %s, channelId: %s, "
         "schedulingType: automatic, %s, "
         "assets: [{ video: { url: %s, metadata: { thumbnailOffset: 1000 } } }] }) { "
         "... on PostActionSuccess { post { id } } "
         "... on MutationError { message } } }"
         % (gstr(text), gstr(channel_id), when, gstr(video_url)))
    st, j = gql(key, q)
    res = (j.get("data") or {}).get("createPost") or {}
    pid = (res.get("post") or {}).get("id")
    return pid, (res.get("message") or (None if pid else "HTTP %s: %s" % (st, j)))


def load(path, default):
    return json.load(open(path)) if os.path.exists(path) else default


def iso(s):
    return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))


def plan(sched, state, start):
    """Items still to hand to Buffer: [(publish_time, item, due_at_or_None)].
    Future slots are pre-scheduled inside Buffer (it publishes them on time even
    if this job never runs again); a slot that just passed is published now."""
    now = datetime.datetime.now(datetime.timezone.utc)
    out = []
    for it in sorted(sched["items"], key=lambda i: i["publishAt"]):
        pub = iso(it["publishAt"])
        if it["video_file"] in state["posted"] or pub < start:
            continue
        if pub > now + datetime.timedelta(minutes=10):
            out.append((pub, it, pub.strftime("%Y-%m-%dT%H:%M:%S.000Z")))
        elif (now - pub) <= DUE_WINDOW:
            out.append((pub, it, None))
        else:
            log("missed slot, not posting late:", it["episode"], it["publishAt"])
    return out[:MAX_QUEUE]


def main():
    key = os.environ.get("BUFFER_API_KEY", "").strip()
    if not key:
        log("Buffer not configured yet (no BUFFER_API_KEY) - skipping."); return
    mode = (os.environ.get("MODE") or "post").strip()
    cfg = load(CONFIG, {})
    start = iso(cfg.get("start_publishAt", "2026-12-16T12:00:00Z"))
    sched = load(SCHEDULE, {"items": []})
    boost = sched.get("_boost", DEFAULT_BOOST)
    state = load(STATE, {"posted": {}})

    if mode == "check":
        chs = channels(key)
        for c in chs:
            log("channel:", c.get("service"), "|", c.get("name"), "| id:", c.get("id"))
        tt = [c for c in chs if "tiktok" in (c.get("service") or "").lower()]
        log("TikTok connected:", "YES" if tt else "NO - connect TikTok in Buffer")
        log("auto-posting starts with items scheduled at/after", start.isoformat())
        todo = plan(sched, state, start)
        log("already handed to Buffer:", len(state["posted"]), "| still to hand over:", len(todo))
        for pub, it, due in todo:
            log("  pending:", it["episode"], it["publishAt"])
        ours = {v.get("buffer_post_id"): v.get("episode") for v in state["posted"].values()}
        for c in tt:
            for due, status, pid in queued_posts(key, c["org"], c["id"]):
                log("  in Buffer:", due, "|", status, "|", ours.get(pid, "(not from this job)"))
        return

    if mode == "validate":
        # Schema check with no side effects: a channel id that is not ours can
        # never publish. "Channel not found"-style reply = request shape is valid;
        # a GraphQL "errors" reply = the shape needs fixing.
        for due in (None, "2027-01-01T00:00:00.000Z"):
            pid, err = create_post(key, "000000000000000000000000", "validation only",
                                   BASES[0] + "02_Thu-Nov26_BO-001.mp4", due)
            log("validate (%s):" % ("scheduled" if due else "now"),
                "UNEXPECTED post %s" % pid if pid else err)
        return

    todo = plan(sched, state, start)
    if not todo:
        log("Nothing new to hand to Buffer."); return
    cid = tiktok_channel(key)
    failed = []
    for pub, it, due in todo:
        text = it["caption"] + boost
        pid, err = None, None
        for base in BASES:
            url = base + it["video_file"]
            log(("scheduling %s for %s" % (it["episode"], due)) if due else
                ("publishing %s now" % it["episode"]), "|", url)
            pid, err = create_post(key, cid, text, url, due)
            if pid or "limit" in (err or "").lower():
                break
            log("  Buffer said:", err)
        if not pid and "limit" in (err or "").lower():
            log("  Buffer queue is full (%s) - the rest go in on a later run." % err)
            break
        if not pid:
            failed.append("%s: %s" % (it["episode"], err)); continue
        state["posted"][it["video_file"]] = {"buffer_post_id": pid, "episode": it["episode"],
                                             "dueAt": due or "now"}
        json.dump(state, open(STATE, "w"), indent=1)
        log("  ok - Buffer post", pid)
    if failed:
        sys.exit("Buffer refused: " + " | ".join(failed))


if __name__ == "__main__":
    main()
