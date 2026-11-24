"""Delete a scheduled FB reel by video id (one-off cleanup of a duplicate).
Set VID below, run via the deletepost workflow. Posts nothing new."""
import meta_common as M

VID = "2034767730548063"   # BO-002 Greenland auto-reel (user posts this one manually)

pid, name, tok, _ = M.resolve()
print("Deleting FB reel", VID, "from", name, "(", pid, ")")
try:
    url = "%s/%s?access_token=%s" % (M.GRAPH, VID, tok)
    r = M._req(url, method="DELETE")
    print("delete result:", r)
except Exception as e:
    print("delete error:", e)

# confirm it's gone from the scheduled list
import datetime
try:
    rows = M.get("%s/scheduled_posts" % pid, tok=tok,
                 fields="id,scheduled_publish_time,message", limit=50).get("data", [])
    print("scheduled_posts now:", len(rows))
    for r in rows:
        spt = r.get("scheduled_publish_time")
        when = datetime.datetime.utcfromtimestamp(int(spt)).strftime("%Y-%m-%d") if spt else "?"
        print("  ", when, "|", (r.get("message") or "")[:45])
except Exception as e:
    print("list error:", e)
