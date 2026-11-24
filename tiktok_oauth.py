"""One-time helper: get a TikTok refresh token for Beyond Obvious auto-posting.

Run this on your own computer (not in CI), once:

    export TIKTOK_CLIENT_KEY=...         # from the TikTok for Developers portal
    export TIKTOK_CLIENT_SECRET=...
    export TIKTOK_REDIRECT_URI=https://example.com/callback   # must match the app
    python tiktok_oauth.py

It prints an authorization URL. Open it, sign in as the Beyond Obvious TikTok
account, and approve. You'll be redirected to your redirect URI with ?code=...
Paste that whole redirected URL back here. The script exchanges the code for a
refresh token, which you then save as the GitHub secret TIKTOK_REFRESH_TOKEN.

Scopes requested: user.info.basic, video.publish, video.upload.
"""
import os
import sys
import json
import urllib.parse
import urllib.request
import urllib.error

OPEN = "https://open.tiktokapis.com"
AUTH = "https://www.tiktok.com/v2/auth/authorize/"
SCOPES = "user.info.basic,video.publish,video.upload"


def main():
    ck = os.environ.get("TIKTOK_CLIENT_KEY")
    cs = os.environ.get("TIKTOK_CLIENT_SECRET")
    redirect = os.environ.get("TIKTOK_REDIRECT_URI")
    if not (ck and cs and redirect):
        sys.exit("Set TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET, TIKTOK_REDIRECT_URI first.")

    params = {"client_key": ck, "response_type": "code", "scope": SCOPES,
              "redirect_uri": redirect, "state": "beyondobvious"}
    print("\n1) Open this URL, sign in as Beyond Obvious, and Authorize:\n")
    print(AUTH + "?" + urllib.parse.urlencode(params))
    print("\n2) You'll be redirected to your redirect URI with ?code=...")
    raw = input("\nPaste the full redirected URL (or just the code): ").strip()

    code = raw
    if "code=" in raw:
        code = urllib.parse.parse_qs(urllib.parse.urlparse(raw).query).get("code", [raw])[0]

    data = urllib.parse.urlencode({
        "client_key": ck, "client_secret": cs, "code": code,
        "grant_type": "authorization_code", "redirect_uri": redirect}).encode()
    req = urllib.request.Request(OPEN + "/v2/oauth/token/", data=data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        j = json.loads(urllib.request.urlopen(req, timeout=60).read().decode())
    except urllib.error.HTTPError as e:
        sys.exit("exchange failed: %s" % e.read().decode()[:500])

    rt = j.get("refresh_token")
    if not rt:
        sys.exit("no refresh_token in response: %s" % j)
    print("\nSUCCESS.")
    print("Save this as the GitHub secret  TIKTOK_REFRESH_TOKEN :\n")
    print(rt)
    print("\n(Valid ~365 days. The daily job auto-rotates it if GH_PAT + GH_REPO are set.)")


if __name__ == "__main__":
    main()
