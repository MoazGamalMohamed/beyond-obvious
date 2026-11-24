"""Safe check: confirms the token resolves the Page + Instagram. Posts nothing."""
import meta_common as M
try:
    pid, name, ptok, ig = M.resolve()
    print("PAGE:", name, "(", pid, ")")
    print("INSTAGRAM:", ig if ig else "NOT LINKED")
    if ig:
        lim = M.get("%s/content_publishing_limit" % ig, tok=ptok, fields="quota_usage,config")
        print("IG publishing quota:", lim.get("data"))
    print("RESULT:", "OK" if ig else "IG_NOT_LINKED")
except Exception as e:
    print("RESULT: ERROR", e)
    raise
