"""Read-only monetization-readiness check for the FB Page and Instagram account.
Posts nothing. Reports account type, profile completeness, and follower counts."""
import meta_common as M

pid, name, ptok, ig = M.resolve()

print("=== FACEBOOK PAGE READINESS ===")
try:
    p = M.get(pid, tok=ptok,
              fields="name,category,about,description,fan_count,followers_count,"
                     "link,is_published,website")
    print("name:", p.get("name"))
    print("category:", p.get("category"))
    print("about:", (p.get("about") or "(EMPTY - add it)"))
    print("description:", (p.get("description") or "(EMPTY - add it)")[:90])
    print("followers:", p.get("followers_count"), "| fans:", p.get("fan_count"))
    print("published:", p.get("is_published"), "| website:", p.get("website") or "(none)")
    print("page link:", p.get("link"))
except Exception as e:
    print("page error:", e)

if ig:
    print("=== INSTAGRAM READINESS ===")
    try:
        i = M.get(ig, tok=ptok,
                  fields="account_type,username,name,biography,media_count,website,"
                         "profile_picture_url")
        print("account_type:", i.get("account_type"), "(want BUSINESS or MEDIA_CREATOR)")
        print("username:", i.get("username"), "| name:", i.get("name") or "(EMPTY)")
        print("biography:", (i.get("biography") or "(EMPTY - add it)"))
        print("media_count:", i.get("media_count"))
        print("website:", i.get("website") or "(EMPTY - add your YouTube/link)")
        print("has_profile_pic:", bool(i.get("profile_picture_url")))
    except Exception as e:
        print("ig basic error:", e)
    try:
        f = M.get(ig, tok=ptok, fields="followers_count")
        print("followers:", f.get("followers_count"))
    except Exception as e:
        print("ig followers (needs insights perm):", e)
else:
    print("=== INSTAGRAM: NOT LINKED ===")
