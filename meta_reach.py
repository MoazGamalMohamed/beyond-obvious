"""Diagnostic: what can the stored META_TOKEN reach? Prints token type, scopes,
and every Facebook Page (+ linked Instagram) it can see. Posts nothing. Used to
decide whether a NEWLY created Page/IG under the same account is already covered.
"""
import meta_common as M

tok = M.token()
try:
    dbg = M.get("debug_token", input_token=tok, access_token=tok).get("data", {})
    print("TOKEN type:", dbg.get("type"), "| app:", dbg.get("app_id"),
          "| expires_at:", dbg.get("expires_at"), "(0 = never)")
    print("SCOPES:", ",".join(dbg.get("scopes", [])))
except Exception as e:
    print("debug_token error:", e)

try:
    pages = M.get("me/accounts", fields="id,name,instagram_business_account{username}").get("data", [])
    print("PAGES VISIBLE:", len(pages))
    for p in pages:
        ig = (p.get("instagram_business_account") or {}).get("username")
        print("  -", p.get("name"), "(", p.get("id"), ") IG:", ig or "none")
    print("VERDICT:",
          "USER-LEVEL (a new Page under this account should appear here after you grant it)"
          if len(pages) >= 1 and dbg.get("type") == "USER"
          else "PAGE-LEVEL (locked to one Page; a new Page needs a fresh token)")
except Exception as e:
    print("me/accounts error:", e)
