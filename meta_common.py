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


def get(path, **params):
    params["access_token"] = token()
    return _req(GRAPH + "/" + path + "?" + urllib.parse.urlencode(params))


def resolve_ids():
    """Return (page_id, page_name, ig_user_id or None) from the Page token."""
    me = get("me", fields="id,name,instagram_business_account")
    page_id = me["id"]
    ig = me.get("instagram_business_account", {}).get("id")
    return page_id, me.get("name", ""), ig


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
