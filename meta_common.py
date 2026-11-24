"""Shared helpers for Beyond Obvious Meta posting (Facebook + Instagram).

One secret is needed: META_TOKEN = a long-lived Facebook Page access token.
From it we resolve the Page id and the linked Instagram business account id at
run time, so nothing else has to be stored.
"""
import os
import sys
import json
import time
import datetime
import urllib.request
import urllib.parse

GV = "v21.0"
GRAPH = "https://graph.facebook.com/" + GV
RUPLOAD_FB = "https://rupload.facebook.com/video-upload/" + GV
RUPLOAD_IG = "https://rupload.facebook.com/ig-api-upload/" + GV


def token():
    t = os.environ.get("META_TOKEN")
    if not t:
        sys.exit("META_TOKEN secret is not set.")
    return t


def _req(url, data=None, headers=None, method=None, raw=None):
    if data is not None:
        data = urllib.parse.urlencode(data).encode()
    body = raw if raw is not None else data
    r = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=300) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        detail = e.read().decode()[:400]
        raise RuntimeError("HTTP %s: %s" % (e.code, detail))


def get(path, tok=None, **params):
    params["access_token"] = tok or token()
    return _req(GRAPH + "/" + path + "?" + urllib.parse.urlencode(params))


# The Beyond Obvious Page id. The token can now see more than one Page (a second
# brand was added to the same business portfolio), so NEVER rely on list order:
# pick the target Page explicitly. Override per brand with the META_PAGE_ID secret.
DEFAULT_PAGE_ID = "1413650968505167"   # Beyond Obvious


def resolve():
    """Resolve the target from META_TOKEN, which may be a USER token or a PAGE token.

    Returns (page_id, page_name, page_token, ig_user_id).
    - If a USER token is stored, /me/accounts lists the Page(s); we select the
      Page whose id is META_PAGE_ID (default: Beyond Obvious) and use its
      (non-expiring) Page token for posting.
    - If a PAGE token is stored, /me/accounts is empty, so we read /me directly.
    """
    data = get("me/accounts",
               fields="id,name,access_token,instagram_business_account").get("data", [])
    if data:
        want = os.environ.get("META_PAGE_ID", "").strip() or DEFAULT_PAGE_ID
        page = next((p for p in data if p["id"] == want), None)
        if page is None:
            names = ", ".join("%s(%s)" % (p.get("name"), p["id"]) for p in data)
            sys.exit("META_PAGE_ID %s not among the Pages this token can see: %s" % (want, names))
        pid = page["id"]
        ptok = page["access_token"]
        ig = page.get("instagram_business_account", {}).get("id")
        return pid, page.get("name", ""), ptok, ig
    # fall back: the stored token is already a Page token
    me = get("me", fields="id,name,instagram_business_account")
    return me["id"], me.get("name", ""), token(), \
        me.get("instagram_business_account", {}).get("id")


# backwards-compatible helper (page token discarded)
def resolve_ids():
    pid, name, _ptok, ig = resolve()
    return pid, name, ig


def load_json(path, default):
    return json.load(open(path)) if os.path.exists(path) else default


def save_json(path, obj):
    json.dump(obj, open(path, "w"), indent=1)


def to_unix(iso_z):
    dt = datetime.datetime.strptime(iso_z, "%Y-%m-%dT%H:%M:%SZ")
    return int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())


def today_chicago():
    """Current date in America/Chicago (CST = UTC-6; no DST in Nov-Mar)."""
    return (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=6)).date()


def log(*a):
    print(datetime.datetime.now().strftime("%H:%M:%S"), *a, flush=True)
