"""List every Facebook Page this token can see + its linked Instagram handle.
Read-only; posts nothing. Used to collect the public FB/IG account URLs for all
brands at once.
"""
import meta_common as M


def main():
    data = M.get("me/accounts",
                 fields="id,name,username,link,"
                        "instagram_business_account{username,name}").get("data", [])
    if not data:
        me = M.get("me", fields="id,name,username,link,"
                                 "instagram_business_account{username,name}")
        data = [me]
    for p in data:
        ig = p.get("instagram_business_account") or {}
        print("PAGE name=%r id=%s username=%r link=%s"
              % (p.get("name"), p.get("id"), p.get("username"), p.get("link")))
        print("   IG username=%r name=%r" % (ig.get("username"), ig.get("name")))


if __name__ == "__main__":
    main()
