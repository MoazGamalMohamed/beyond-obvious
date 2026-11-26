# Idiom Zoo — free song generation on Kaggle GPU

The sung tracks (Kiki + Bruno) are made with **ACE-Step v1.5 XL-Turbo**, the same
model behind *Break the Ice*, IZ-001 and IZ-002. Two free paths, kept in parallel:

| Path | Where it runs | Quota | Role |
|------|---------------|-------|------|
| **Kaggle GPU** | GitHub Actions → Kaggle kernel on Kaggle's free GPU | 30 GPU-h/week | primary (fast, reliable) |
| **ZeroGPU** | render container (`gen_all.py`, `victor/ace-step-jam`) | small daily cap | fallback |

Both call the identical generation code, so the output sounds the same.

## How the Kaggle path works

1. `generate_iz_kaggle.yml` (manual dispatch) runs `gen_kaggle_iz.py`.
2. It reads `songsrc_idiomzoo/*.json` (one file per episode: `slug`, `bpm`,
   `seed`, `lyrics`) and finds any song missing from `songs_idiomzoo/`.
3. It pushes a Kaggle **script kernel** (`kaggle_assets/iz_kaggle_batch_template.py`)
   that clones the `victor/ace-step-jam` Space and runs its
   `AceStepHandler.generate_music(...)` on Kaggle's own GPU — **no ZeroGPU quota**.
   Generation params are copied verbatim from the Space: 8 steps, `guidance=7.0`,
   `infer_method="ode"`, `shift=1.0`, `vocal_language="en"`, 58 s.
4. It polls the kernel, downloads each `<slug>.wav`, and commits it to
   `songs_idiomzoo/`.
5. The render container picks up `songs_idiomzoo/<slug>.wav`, then aligns
   (Whisper), masters, and renders the video with the episode's scene pack.

## One-time setup (repo secrets)

Add under **Settings → Secrets and variables → Actions → Secrets**:

- `KAGGLE_API_TOKEN` — the single access token (`KGAT_...`) from
  Kaggle → Settings → API → **Generate New Token**. This is the auth.
- `KAGGLE_USERNAME` — your Kaggle username *slug* (from your profile URL
  `kaggle.com/<slug>`, or Kaggle → Settings → Account). Needed to name the kernel
  under your account. Not sensitive — may live under the Variables tab instead.
- `HF_TOKEN` — *optional*, only if the model download needs auth.

Legacy fallback: if an old-style `kaggle.json` (username + key) is used instead,
set `KAGGLE_USERNAME` + `KAGGLE_KEY` and omit `KAGGLE_API_TOKEN`.

The Kaggle account must be **phone-verified** (Kaggle → Settings) to use GPU +
internet in kernels.

## Run

Dispatch **"Generate songs on Kaggle GPU - Idiom Zoo"**. It is idempotent: songs
already in `songs_idiomzoo/` are skipped, so re-dispatching only fills gaps.
