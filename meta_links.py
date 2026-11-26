"""Print public permalinks for the Meta posts recorded in the state files.

Reads the Instagram and Facebook state files (video_file -> id), then asks the
Graph API for each post's public URL. Read-only; posts nothing. Pin the brand
with META_PAGE_ID (same as the posting workflows).
"""
import os
import json
import meta_common as M

HERE = os.path.dirname(os.path.abspath(__file__))


def _load(name):
    p = os.path.join(HERE, name)
    return json.load(open(p)) if os.path.exists(p) else {"posted": {}}


def main():
    page_id, name, tok, ig = M.resolve()
    M.log("Page:", name, page_id, "| IG:", ig)
    ig_state = _load(os.environ.get("IG_STATE", "state_idiomzoo_ig.json"))
    fb_state = _load(os.environ.get("FB_STATE", "state_idiomzoo_fb.json"))

    for vf, mid in ig_state.get("posted", {}).items():
        try:
            r = M.get(str(mid), tok=tok, fields="permalink")
            print("IG  %-22s %s" % (vf, r.get("permalink", "(no permalink)")))
        except Exception as e:
            print("IG  %-22s ERROR %s" % (vf, e))

    for vf, vid in fb_state.get("posted", {}).items():
        try:
            r = M.get(str(vid), tok=tok, fields="permalink_url")
            pu = r.get("permalink_url", "")
            if pu.startswith("/"):
                pu = "https://www.facebook.com" + pu
            print("FB  %-22s %s" % (vf, pu or "(no permalink)"))
        except Exception as e:
            print("FB  %-22s ERROR %s" % (vf, e))


if __name__ == "__main__":
    main()
