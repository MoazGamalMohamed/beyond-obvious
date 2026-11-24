"""Fill out the Facebook Page's About + Description via the Graph API.
(IG bio and profile images can't be set via the API — see BRAND_SETUP.md.)
Idempotent: safe to re-run."""
import meta_common as M

pid, name, ptok, ig = M.resolve()

ABOUT = ("Funny 60-second science. Two cartoon characters explain the surprising "
         "physics, engineering, and geography behind everyday things. New short every day.")
DESC = ("Beyond Obvious turns big science into bite-sized cartoons. Every day, Noodle "
        "(the overconfident one) and Pip (the deadpan know-it-all) tackle a question you "
        "didn't know you had - why ice floats, how steel ships don't sink, why the Moon "
        "hides one face - in under a minute. Animated, fact-checked, and genuinely funny. "
        "Follow for a daily dose of 'wait, really?'")

print("Updating Page:", name, "(", pid, ")")
try:
    r = M._req("%s/%s" % (M.GRAPH, pid),
               data={"access_token": ptok, "about": ABOUT, "description": DESC},
               method="POST")
    print("UPDATE result:", r)
except Exception as e:
    print("UPDATE error (likely missing pages_manage_metadata):", e)

try:
    cur = M.get(pid, tok=ptok,
                fields="about,description,category,link,fan_count,followers_count")
    print("NOW about:", cur.get("about"))
    print("NOW description:", (cur.get("description") or "")[:140])
    print("NOW category:", cur.get("category"), "| followers:", cur.get("followers_count"))
except Exception as e:
    print("readback error:", e)
