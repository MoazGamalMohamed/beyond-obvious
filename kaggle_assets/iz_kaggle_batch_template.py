"""Idiom Zoo song generation on Kaggle's free GPU.

Runs the EXACT generation code of the Hugging Face Space `victor/ace-step-jam`
(ACE-Step v1.5 XL-Turbo) on Kaggle's own GPU, so the output matches the songs we
already approved (Break the Ice, IZ-001, IZ-002) with NO ZeroGPU quota involved.

The orchestrator (gen_kaggle_iz.py) substitutes the pending episodes into
__EPISODES_JSON__ before pushing this as a Kaggle script kernel.

Generation parameters are copied verbatim from the Space's _run_inference():
    generate_music(captions, lyrics, audio_duration, inference_steps=8,
                   guidance_scale=7.0, use_random_seed=False, seed=<seed>,
                   infer_method="ode", shift=1.0, use_adg=False, vocal_language="en")
and the audio is extracted exactly as the Space does
(result["audios"][0]["tensor"] / ["sample_rate"], peak-normalised to 0.95).
"""
import os, sys, json, base64, subprocess, traceback
import numpy as np
import soundfile as sf

WORK = "/kaggle/working"          # outputs only (20 GB cap, downloaded afterwards)
SCRATCH = "/tmp/iz_acestep"         # big scratch disk: Space clone + model weights
SPACE = os.path.join(SCRATCH, "acestep_space")
os.makedirs(SCRATCH, exist_ok=True)
os.environ.setdefault("HF_HOME", os.path.join(SCRATCH, "hf_home"))
SPACE_REPO = "https://huggingface.co/spaces/victor/ace-step-jam"

# Same base style tags the ZeroGPU path uses (gen_all.py); BPM appended per episode.
BASE_TAGS = ("playful indie pop, upbeat, cheerful, bright female lead vocal, clear enunciation, "
             "ukulele, acoustic guitar, hand claps, light bouncy drums, glockenspiel, "
             "kids educational singalong, catchy chorus hook, sunny, warm, wholesome")

# ---- episodes injected by the orchestrator (base64 JSON, quote-safe) ----
EPISODES = json.loads(base64.b64decode("__EPISODES_B64__").decode("utf-8"))


def sh(cmd):
    print("+", cmd, flush=True)
    subprocess.check_call(cmd, shell=True)


def setup():
    """Clone the Space (for its vendored `acestep` package) and install its deps.
    Keep Kaggle's CUDA-matched torch/torchaudio/torchvision instead of the pinned
    ones, so the GPU wheels stay compatible with Kaggle's driver.
    """
    if not os.path.isdir(SPACE):
        sh(f"git clone --depth 1 {SPACE_REPO} {SPACE}")
    req_in = os.path.join(SPACE, "requirements.txt")
    req_out = os.path.join(SCRATCH, "reqs_filtered.txt")
    # Keep Kaggle's CUDA-matched torch stack; drop only the Gradio-server/app-only
    # deps. `spaces` is kept (tiny, and some handler builds import it; it no-ops off
    # Hugging Face ZeroGPU infra, so direct generate_music() runs on Kaggle's GPU).
    skip = ("torch==", "torchaudio==", "torchvision==", "gradio", "uvicorn", "fastapi", "openai")
    with open(req_in) as f, open(req_out, "w") as g:
        for line in f:
            s = line.strip()
            if not s or s.startswith("#"):
                continue
            if s.lower().startswith(skip):
                continue
            g.write(s + "\n")
    sh(f"pip -q install -r {req_out}")
    sys.path.insert(0, SPACE)


def extract_wav(result):
    """Reproduce the Space's _run_inference() audio handling exactly."""
    if not result.get("success"):
        raise RuntimeError(result.get("error", "generation failed"))
    audio = result["audios"][0]
    tensor = audio["tensor"]
    sr = audio["sample_rate"]
    data = tensor.cpu().float().numpy()
    if data.ndim == 2:
        data = data.T
        if data.shape[1] == 1:
            data = data[:, 0]
    peak = np.abs(data).max()
    if peak > 1e-4:
        data = (data / peak * 0.95).astype(np.float32)
    return data, sr


def main():
    subprocess.call("df -h /kaggle/working /tmp; nvidia-smi -L", shell=True)
    setup()
    from acestep.handler import AceStepHandler

    storage = os.path.join(SCRATCH, "_storage")
    os.makedirs(storage, exist_ok=True)
    handler = AceStepHandler(persistent_storage_path=storage)
    status, ready = handler.initialize_service(
        project_root=SPACE,
        config_path="acestep-v15-xl-turbo",
        device="auto",
        use_flash_attention=handler.is_flash_attention_available(),
        compile_model=False,
        offload_to_cpu=False,
        offload_dit_to_cpu=False,
    )
    print("initialize_service:", status, ready, flush=True)
    subprocess.call("df -h /kaggle/working /tmp", shell=True)
    if not ready:
        print("MODEL NOT READY - aborting before generation", flush=True)
        sys.exit(1)

    done = []
    for ep in EPISODES:
        slug = ep["slug"]
        seed = int(ep.get("seed", 1337))
        tags = f"{BASE_TAGS}, {int(ep['bpm'])} BPM"
        print(f"=== generating {ep.get('episode', slug)} ({slug}) seed={seed} ===", flush=True)
        try:
            result = handler.generate_music(
                captions=tags,
                lyrics=ep["lyrics"],
                audio_duration=58.0,
                inference_steps=8,
                guidance_scale=7.0,
                use_random_seed=False,
                seed=seed,
                infer_method="ode",
                shift=1.0,
                use_adg=False,
                vocal_language="en",
            )
            data, sr = extract_wav(result)
            out = os.path.join(WORK, f"{slug}.wav")
            sf.write(out, data, sr)
            print(slug, "OK", out, os.path.getsize(out), "bytes", "sr=", sr, flush=True)
            done.append(slug)
        except Exception as e:
            print(slug, "ERROR", type(e).__name__, str(e)[:400], flush=True)
            traceback.print_exc()

    print("DONE generated=", done, flush=True)
    if not done:
        sys.exit(1)


if __name__ == "__main__":
    main()
