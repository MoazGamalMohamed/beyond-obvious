"""Safe check: confirms the token resolves the Page + Instagram. Posts nothing."""
import meta_common as M
try:
    pid, name, ig = M.resolve_ids()
    print("PAGE:", name, "(", pid, ")")
    print("INSTAGRAM:", ig if ig else "NOT LINKED")
    # also show publishing quota (read-only)
    if ig:
        lim = M.get("%s/content_publishing_limit" % ig, fields="config,quota_usage")
        print("IG publishing quota:", lim.get("data"))
    print("RESULT:", "OK" if ig else "IG_NOT_LINKED")
except Exception as e:
    print("RESULT: ERROR", e)
    raise
