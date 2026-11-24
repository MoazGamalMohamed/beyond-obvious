"""Safe check: confirms the token resolves the Page + Instagram. Posts nothing."""
import meta_common as M
try:
    pid, name, ptok, ig = M.resolve()
    print("PAGE:", name, "(", pid, ")")
    print("INSTAGRAM:", ig if ig else "NOT LINKED")
    if ig:
        lim = M.get("%s/content_publishing_limit" % ig, tok=ptok, fields="quota_usage,config")
        print("IG publishing quota:", lim.get("data"))
    # report the stored token's type + expiry (for longevity)
    import datetime
    dbg = M.get("debug_token", input_token=M.token()).get("data", {})
    ea = dbg.get("expires_at")
    when = "never" if not ea else datetime.datetime.utcfromtimestamp(ea).strftime("%Y-%m-%d")
    print("STORED TOKEN type:", dbg.get("type"), "| expires:", when)
    print("RESULT:", "OK" if ig else "IG_NOT_LINKED")
except Exception as e:
    print("RESULT: ERROR", e)
    raise
