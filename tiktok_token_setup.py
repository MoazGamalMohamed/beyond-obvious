"""One-time TikTok token setup, run from the "TikTok token setup" workflow so you
never need a terminal.

MODE=url       -> prints the authorization URL. Open it, approve as Beyond Obvious,
                  then copy the  code=  value from the address bar you land on.
MODE=exchange  -> exchanges AUTH_CODE for a refresh token and stores it as the repo
                  secret TIKTOK_REFRESH_TOKEN (needs GH_PAT with Secrets: write).
                  The token itself is never printed.

Env: MODE, REDIRECT_URI, AUTH_CODE, TIKTOK_CLIENT_KEY, TIKTOK_CLIENT_SECRET,
     GH_PAT, GH_REPO.
"""
import os
import sys
import urllib.parse
import tiktok_common as T

AUTH = "https://www.tiktok.com/v2/auth/authorize/"
SCOPES = "user.info.basic,video.publish,video.upload"


def main():
    mode = os.environ.get("MODE", "url").strip()
    ck = T._env("TIKTOK_CLIENT_KEY")
    redirect = T._env("REDIRECT_URI")

    if mode == "url":
        params = {"client_key": ck, "response_type": "code", "scope": SCOPES,
                  "redirect_uri": redirect, "state": "beyondobvious"}
        print("\n================  AUTHORIZE URL  ================")
        print("Open this, sign in as Beyond Obvious, and Authorize.")
        print("Then copy the  code=...  value from the address bar you land on.\n")
        print(AUTH + "?" + urllib.parse.urlencode(params))
        print("================================================\n")
        return

    if mode == "exchange":
        cs = T._env("TIKTOK_CLIENT_SECRET")
        code = T._env("AUTH_CODE")
        if "code=" in code:
            code = urllib.parse.parse_qs(urllib.parse.urlparse(code).query).get("code", [code])[0]
        code = urllib.parse.unquote(code).strip()
        st, j = T._req(T.OPEN + "/v2/oauth/token/",
                       data={"client_key": ck, "client_secret": cs, "code": code,
                             "grant_type": "authorization_code", "redirect_uri": redirect},
                       headers={"Content-Type": "application/x-www-form-urlencoded"})
        rt = j.get("refresh_token")
        if not rt:
            sys.exit("exchange failed (HTTP %s): %s" % (st, j))
        ok, msg = T.write_repo_secret("TIKTOK_REFRESH_TOKEN", rt)
        if not ok:
            sys.exit("got the token but could not store it (%s). Make sure GH_PAT "
                     "(with Secrets: write) is set as a secret." % msg)
        print("SUCCESS:", msg)
        print("TikTok refresh token is now stored. You're ready for the test post.")
        return

    sys.exit("unknown MODE %r (use url or exchange)" % mode)


if __name__ == "__main__":
    main()
