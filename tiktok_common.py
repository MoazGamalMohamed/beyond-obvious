"""Shared helpers for Beyond Obvious TikTok auto-posting (Content Posting API v2).

GitHub Actions secrets this uses:
  TIKTOK_CLIENT_KEY     - app client key   (TikTok for Developers portal)
  TIKTOK_CLIENT_SECRET  - app client secret
  TIKTOK_REFRESH_TOKEN  - OAuth refresh token (get once via tiktok_oauth.py)
  TIKTOK_PRIVACY        - optional: SELF_ONLY (default, pre-audit) or
                          PUBLIC_TO_EVERYONE (after the app passes TikTok's audit)
  GH_PAT + GH_REPO      - optional but recommended: lets the daily job write the
                          rotated refresh token back into the repo secret, so it
                          stays hands-free. GH_PAT = fine-grained PAT with
                          "Secrets: write" on this repo; GH_REPO = owner/name.

No third-party Python needed except pynacl, and only when GH_PAT is set (to
encrypt the rotated secret). Everything else is standard library.
"""
import os
import sys
import json
import base64
import datetime
import urllib.request
import urllib.parse
import urllib.error

OPEN = "https://open.tiktokapis.com"


def _req(url, data=None, headers=None, method=None, raw=None, timeout=300):
    """Minimal HTTP. Returns (status_code, parsed_json)."""
    if data is not None and raw is None:
        data = urllib.parse.urlencode(data).encode()
    body = raw if raw is not None else data
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            txt = r.read().decode() or "{}"
            try:
                return r.getcode(), json.loads(txt)
            except ValueError:
                return r.getcode(), {"_raw": txt}
    except urllib.error.HTTPError as e:
        return e.code, {"_error": e.read().decode()[:600]}


def _env(name, required=True):
    v = os.environ.get(name)
    if required and not v:
        sys.exit("%s is not set." % name)
    return v


def log(*a):
    print(datetime.datetime.now().strftime("%H:%M:%S"), *a, flush=True)


def refresh_access_token():
    """Exchange the stored refresh token for a fresh access token.
    TikTok rotates the refresh token on each refresh, so persist the new one."""
    ck, cs = _env("TIKTOK_CLIENT_KEY"), _env("TIKTOK_CLIENT_SECRET")
    rt = _env("TIKTOK_REFRESH_TOKEN")
    code, j = _req(OPEN + "/v2/oauth/token/",
                   data={"client_key": ck, "client_secret": cs,
                         "grant_type": "refresh_token", "refresh_token": rt},
                   headers={"Content-Type": "application/x-www-form-urlencoded"})
    if "access_token" not in j:
        sys.exit("token refresh failed (HTTP %s): %s" % (code, j))
    _maybe_rotate(j.get("refresh_token"), rt)
    return j["access_token"], j.get("open_id")


def write_repo_secret(name, value):
    """Encrypt `value` with the repo's Actions public key and store it as the
    GitHub secret `name`. Needs GH_PAT (Secrets: write) + GH_REPO. The value is
    never printed. Returns (ok: bool, message: str)."""
    pat, repo = os.environ.get("GH_PAT"), os.environ.get("GH_REPO")
    if not (pat and repo):
        return False, "GH_PAT + GH_REPO not set"
    try:
        import nacl.public
        import nacl.encoding
    except ImportError:
        return False, "pynacl not installed"
    api = "https://api.github.com/repos/%s/actions/secrets" % repo
    hdr = {"Authorization": "Bearer " + pat, "Accept": "application/vnd.github+json",
           "User-Agent": "beyond-obvious-bot", "X-GitHub-Api-Version": "2022-11-28"}
    code, key = _req(api + "/public-key", headers=hdr)
    if "key" not in key:
        return False, "could not read repo public key (HTTP %s): %s" % (code, key)
    pk = nacl.public.PublicKey(key["key"].encode(), nacl.encoding.Base64Encoder())
    sealed = nacl.public.SealedBox(pk).encrypt(value.encode())
    enc = base64.b64encode(sealed).decode()
    code, _ = _req(api + "/" + name,
                   raw=json.dumps({"encrypted_value": enc, "key_id": key["key_id"]}).encode(),
                   headers={**hdr, "Content-Type": "application/json"}, method="PUT")
    if code not in (201, 204):
        return False, "secret write failed (HTTP %s)" % code
    return True, "stored secret %s (HTTP %s)" % (name, code)


def _maybe_rotate(new_rt, old_rt):
    """If the refresh token changed, persist the new one to the repo secret so the
    next run keeps working. Falls back to a masked note if GH_PAT isn't set."""
    if not new_rt or new_rt == old_rt:
        return
    ok, msg = write_repo_secret("TIKTOK_REFRESH_TOKEN", new_rt)
    if ok:
        log("refresh token rotated and persisted:", msg)
    else:
        log("NOTE: refresh token rotated but not auto-persisted (%s)." % msg)
        log("      Set GH_PAT + GH_REPO so this happens automatically.")


def load_json(path, default):
    return json.load(open(path)) if os.path.exists(path) else default


def save_json(path, obj):
    json.dump(obj, open(path, "w"), indent=1)
