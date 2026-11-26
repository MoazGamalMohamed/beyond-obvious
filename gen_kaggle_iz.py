#!/usr/bin/env python3
"""Generate Idiom Zoo songs on Kaggle's free GPU, from GitHub Actions.

Reads songsrc_idiomzoo/*.json (episode = slug + bpm + seed + lyrics), figures out
which songs are still missing from songs_idiomzoo/, and generates them by pushing a
Kaggle SCRIPT kernel that runs the ACE-Step v1.5 XL-Turbo code of the
`victor/ace-step-jam` Space on Kaggle's own GPU. No ZeroGPU quota is used, so this
is the "always available" path; the ZeroGPU Space (gen_all.py in the render
container) stays wired as the fallback.

Env (GitHub Actions secrets):
  KAGGLE_USERNAME, KAGGLE_KEY   (required)
  HF_TOKEN                      (optional; forwarded only if the model needs auth)

Idempotent: a song already present in songs_idiomzoo/ is skipped. The kernel is a
single reusable slug per account, re-run on each dispatch.
"""
import os
import sys
import json
import time
import glob
import base64
import shutil
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "songsrc_idiomzoo")
OUT = os.path.join(HERE, "songs_idiomzoo")
TPL = os.path.join(HERE, "kaggle_assets", "iz_kaggle_batch_template.py")
PUSH = os.path.join(HERE, "_kaggle_push")
DL = os.path.join(HERE, "_kaggle_out")
KERNEL_SLUG = "iz-acestep-gen"
MINBYTES = 100_000
POLL_SECONDS = 30
TIMEOUT_MIN = 50


def log(*a):
    print(*a, flush=True)


def setup_auth():
    """Authenticate the Kaggle CLI and return the account username.

    The username is required to name the kernel <username>/<slug>. Auth supports
    both Kaggle credential styles:
      - NEW: a single access token in KAGGLE_API_TOKEN (format KGAT_...), written
        to ~/.kaggle/access_token (the client reads it automatically).
      - LEGACY: KAGGLE_USERNAME + KAGGLE_KEY, written to ~/.kaggle/kaggle.json.
    """
    d = os.path.expanduser("~/.kaggle")
    os.makedirs(d, exist_ok=True)
    user = os.environ.get("KAGGLE_USERNAME", "").strip()
    token = os.environ.get("KAGGLE_API_TOKEN", "").strip()
    key = os.environ.get("KAGGLE_KEY", "").strip()

    if token:
        p = os.path.join(d, "access_token")
        with open(p, "w") as f:
            f.write(token)
        os.chmod(p, 0o600)
        os.environ["KAGGLE_API_TOKEN"] = token
        log("auth: KAGGLE_API_TOKEN")
    elif user and key:
        p = os.path.join(d, "kaggle.json")
        with open(p, "w") as f:
            json.dump({"username": user, "key": key}, f)
        os.chmod(p, 0o600)
        log("auth: KAGGLE_USERNAME + KAGGLE_KEY (legacy)")
    else:
        log("ERROR: no Kaggle auth. Add KAGGLE_API_TOKEN (and KAGGLE_USERNAME) as repo secrets.")
        sys.exit(78)

    if not user:
        log("ERROR: KAGGLE_USERNAME not set - needed to name the kernel under your account.")
        sys.exit(78)
    return user


def pending():
    eps = []
    for f in sorted(glob.glob(os.path.join(SRC, "*.json"))):
        e = json.load(open(f))
        wav = os.path.join(OUT, e["slug"] + ".wav")
        if not (os.path.exists(wav) and os.path.getsize(wav) > MINBYTES):
            eps.append(e)
    return eps


def build_push_dir(user, eps):
    if os.path.isdir(PUSH):
        shutil.rmtree(PUSH)
    os.makedirs(PUSH)
    b64 = base64.b64encode(json.dumps(eps).encode("utf-8")).decode("ascii")
    body = open(TPL).read().replace("__EPISODES_B64__", b64)
    with open(os.path.join(PUSH, "iz_kaggle_batch.py"), "w") as f:
        f.write(body)
    meta = {
        "id": f"{user}/{KERNEL_SLUG}",
        "title": "IZ ACE-Step gen",
        "code_file": "iz_kaggle_batch.py",
        "language": "python",
        "kernel_type": "script",
        "is_private": True,
        "enable_gpu": True,
        "enable_internet": True,
    }
    with open(os.path.join(PUSH, "kernel-metadata.json"), "w") as f:
        json.dump(meta, f, indent=1)


def run(cmd):
    log("+", " ".join(cmd))
    return subprocess.run(cmd, capture_output=True, text=True)


def main():
    eps = pending()
    if not eps:
        log("Nothing pending - all songs already in songs_idiomzoo/.")
        return 0
    user = setup_auth()
    log("pending:", [e["slug"] for e in eps])
    build_push_dir(user, eps)

    r = run(["kaggle", "kernels", "push", "-p", PUSH])
    log(r.stdout.strip())
    if r.stderr.strip():
        log("stderr:", r.stderr.strip())
    kid = f"{user}/{KERNEL_SLUG}"

    # The CLI prints e.g.  <ref> has status "complete"  (also: queued, running,
    # error, cancelRequested, cancelAcknowledged). Match the quoted state word.
    deadline = time.time() + TIMEOUT_MIN * 60
    status = ""
    while time.time() < deadline:
        time.sleep(POLL_SECONDS)
        r = run(["kaggle", "kernels", "status", kid])
        out = (r.stdout + r.stderr).strip()
        log(out)
        low = out.lower()
        if '"complete"' in low:
            status = "complete"
            break
        if '"error"' in low or '"cancel' in low:
            status = "error"
            break
        # otherwise queued/running -> keep polling
    if status != "complete":
        log("Kernel did not complete in time (status:", status or "timeout", ").")
        return 2

    if os.path.isdir(DL):
        shutil.rmtree(DL)
    os.makedirs(DL)
    r = run(["kaggle", "kernels", "output", kid, "-p", DL])
    log(r.stdout.strip())
    if r.stderr.strip():
        log("stderr:", r.stderr.strip())

    os.makedirs(OUT, exist_ok=True)
    got = []
    for e in eps:
        src = os.path.join(DL, e["slug"] + ".wav")
        if os.path.exists(src) and os.path.getsize(src) > MINBYTES:
            shutil.copy(src, os.path.join(OUT, e["slug"] + ".wav"))
            got.append(e["slug"])
        else:
            log("missing output for", e["slug"])
    log("downloaded:", got)
    return 0 if got else 3


if __name__ == "__main__":
    sys.exit(main())
