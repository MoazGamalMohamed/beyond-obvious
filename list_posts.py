"""Read-only: list what is already published OR scheduled on the FB Page and
Instagram. Posts nothing. Used to double-check which videos were posted manually."""
import datetime
import meta_common as M

pid, name, ptok, ig = M.resolve()

print("=== FACEBOOK SCHEDULED (unpublished) ===")
for edge in ("scheduled_posts", "video_reels"):
    try:
        params = dict(limit=50)
        if edge == "scheduled_posts":
            params["fields"] = "id,scheduled_publish_time,message"
        else:
            # include unpublished reels and their scheduled time
            params["fields"] = "id,title,description,created_time,scheduled_publish_time,is_published"
        rows = M.get("%s/%s" % (pid, edge), tok=ptok, **params).get("data", [])
        print(edge, ":", len(rows))
        for r in rows:
            spt = r.get("scheduled_publish_time")
            when = datetime.datetime.utcfromtimestamp(int(spt)).strftime("%Y-%m-%d %H:%MZ") if spt else "?"
            txt = (r.get("message") or r.get("description") or r.get("title") or "").replace("\n", " ")[:55]
            print("  ", edge, r.get("id"), "sched=" + when, "pub=" + str(r.get("is_published")), "|", txt)
    except Exception as e:
        print("  ", edge, "error:", e)

print("=== FACEBOOK PAGE:", name, "(", pid, ") ===")
try:
    reels = M.get("%s/video_reels" % pid, tok=ptok,
                  fields="id,title,description,created_time", limit=25).get("data", [])
    print("Published reels:", len(reels))
    for r in reels:
        txt = (r.get("description") or r.get("title") or "").replace("\n", " ")[:70]
        print("  REEL", r.get("id"), r.get("created_time"), "|", txt)
except Exception as e:
    print("  reels error:", e)
try:
    feed = M.get("%s/feed" % pid, tok=ptok,
                 fields="id,message,created_time,status_type", limit=25).get("data", [])
    print("Feed posts:", len(feed))
    for p in feed:
        txt = (p.get("message") or "").replace("\n", " ")[:70]
        print("  POST", p.get("id"), p.get("created_time"), p.get("status_type"), "|", txt)
except Exception as e:
    print("  feed error:", e)

if ig:
    print("=== INSTAGRAM:", ig, "===")
    try:
        media = M.get("%s/media" % ig, tok=ptok,
                      fields="id,caption,media_type,timestamp,permalink", limit=25).get("data", [])
        print("IG media:", len(media))
        for m in media:
            txt = (m.get("caption") or "").replace("\n", " ")[:70]
            print("  MEDIA", m.get("id"), m.get("media_type"), m.get("timestamp"),
                  "|", txt, "|", m.get("permalink"))
    except Exception as e:
        print("  ig media error:", e)
