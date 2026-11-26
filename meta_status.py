"""Report the real published/scheduled status of the FB reels in a state file.

Read-only. For each video_file -> id in STATE_FILE, asks the Graph API whether
it is published or still scheduled (and when), plus its public permalink.
"""
import os
import json
import datetime
import meta_common as M

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    page_id, name, tok, ig = M.resolve()
    M.log("Page:", name, page_id)
    state = json.load(open(os.path.join(HERE, os.environ.get("STATE_FILE", "state_fb.json"))))
    now = datetime.datetime.now(datetime.timezone.utc)
    live = sched = 0
    for vf, vid in state.get("posted", {}).items():
        try:
            r = M.get(str(vid), tok=tok,
                      fields="id,published,scheduled_publish_time,permalink_url,created_time")
            sp = r.get("scheduled_publish_time")
            spix = ""
            if sp:
                spix = datetime.datetime.utcfromtimestamp(int(sp)).strftime("%Y-%m-%dT%H:%M:%SZ")
            pub = r.get("published")
            if pub is True and not (sp and int(sp) > now.timestamp()):
                live += 1
            else:
                sched += 1
            print("%-34s published=%s scheduled=%s url=%s"
                  % (vf, pub, spix or "-", r.get("permalink_url") or "-"))
        except Exception as e:
            print("%-34s ERROR %s" % (vf, e))
    M.log("LIVE now:", live, "| still scheduled:", sched)


if __name__ == "__main__":
    main()
