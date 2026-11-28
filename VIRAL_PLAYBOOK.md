# Viral Playbook — titles, first frames & long-form

Standing content rule for **all three brands** (Beyond Obvious, What If Lab, Idiom Zoo).
Every new episode must follow this for both the **on-platform title** (the first line of
its `caption`, and the YouTube title) and the **first frame / thumbnail** (the rendered
`cover_overlay`). For **long-form episodes** (7–12 min), also follow the showrunner brief in §5.
Keep each brand's voice and characters separate — same *technique*, not the same content.

> Origin: moaz compared our shorts to the viral ones in his feed
> (2026-11-28). Theirs pulled the eye; ours read like a textbook caption.
> §5 added 2026-11-28 from moaz's showrunner prompt for long-form episodes.

## 1. Titles — open a curiosity gap, never spoil the answer

The whole job of the title is to make someone *need* to watch. The viral references work
because the payoff is withheld:

- "Why He Puts Bombs on the Railroad Track"  ← you have no idea why → you click
- "How Did Ancient Humans Sleep Without AC? 🥵"
- "What Would Happen If Africa Split In Two?"

**Do**
- Lead with the surprising question, or a concrete almost-unbelievable claim.
- Keep it short and concrete. Favor "Why / How / What would happen if…".
- Make it personal/visual where you can ("He", "You", a named thing).
- At most **one** emoji, for emotion (🥵, 🤯), not decoration.
- Leave the mechanism *out* — the video is the reveal.

**Don't**
- Don't answer the question in the title. ❌ "Winter = Earth far from the Sun? Nope."
  (This tells them the answer is *no* before they watch.)
  ✅ "If winter isn't the Sun pulling away, what is it? ❄️"
- Don't sound like a lesson. ❌ "What does BREAK THE ICE really mean?"
  ✅ "He said 'break the ice' — so why is everyone frozen? 🧊"
- No emoji soup, no hashtag stuffing in the first line.

## 2. First frame / thumbnail — a tempting, character-driven scene

The first rendered frame IS the thumbnail in the feed. It must look like a moment you
walked in on, not a title card.

**Do**
- Put the brand character **mid-action** in an intriguing situation. Each brand has its
  own cast — never mix them:
  - **Beyond Obvious** = NOODLE (with Pip).
  - **What If Lab** = **Watt**, the lab's single curious mascot.
  - **Idiom Zoo** = Kiki 🦜 & Bruno 🐶 (first frame: Bruno mid-way through taking the idiom literally).
- Show tension or a question on screen, not the explanation.
- Big, readable cover line that teases (≤ ~5 words). Clear figure/ground.

**Don't**
- No static logo/plain-text card as frame 1.
- Don't reveal the payoff in the cover text.
- Fredoka (the render font) has **no arrow / ≈ / emoji glyphs** — in *rendered* text use
  words, ":" and "~". (Emoji are fine in the *platform caption*, just not baked into video.)

## 3. Where this lives in the pipeline

- Platform title  = first line of each item's `caption` in the schedule JSON
  (`schedule.json` for BO, `schedule_whatiflab.json`, `schedule_idiomzoo_*.json`).
- First frame/thumbnail = `cover_overlay` + `META(..., cap_y=…)` in each
  `src/episodes/epNNN_*.py` module (and the WL/IZ equivalents; WL brand kit = `wif_brand.py`).
- Idiom Zoo: `iz_engine.draw_cover()` renders the cold open (first ~0.5–1.2 s): the pack's
  *gag* scene ~1 s in (Bruno mid-gag) + the episode's `cover` line from `idiom_bank.json`
  (falls back to `hook_text`). The old "IDIOM ZOO" logo card is gone. Each bank entry also
  carries its platform `title` (hook first, then the idiom in quotes for search, 1 emoji).
- Already-rendered, already-scheduled videos keep their covers unless re-rendered;
  retitling their captions (unposted items only) is safe and reversible.

## 4. Checklist before scheduling any new episode

- [ ] Title opens a curiosity gap and does NOT contain the answer.
- [ ] ≤ 1 emoji in the title; concrete and short.
- [ ] First frame shows a character mid-action, cover line teases only.
- [ ] Brand voice/characters not mixed with another brand.

## 5. Long-form episodes (7–12 min) — showrunner brief

For full episodes on YouTube + Facebook. The title/first-frame rules in §1–2 still govern the
thumbnail and the YouTube title. Keep each brand's brief separate.

### Shared craft (all three brands)
- **Earn the click, then pay it off.** The thumbnail is a promise; the first payoff must deliver
  it. Treat virality as an outcome we *measure*, never promise or fake.
- **First 20 seconds:** establish who wants what and why it might go wrong. Deliver an early
  payoff, *then* add a complication.
- **Show the result before the explanation.** Let the viewer judge the evidence / joke
  themselves; cut any explanation that arrives after they already got it.
- **Let silence play.** A held beat, a glance, room tone before a confession does more than
  another line. Trim runtime whenever the story earns a shorter cut.
- **Reject a premise whose thumbnail beats its ending.** If the best moment is the title, don't
  make it.
- **Prove the hardest 30–45 s first** (picture *and* sound) at release quality before rendering
  the rest. If it fails at phone size, change blocking / camera / script / voices / animation
  and redo — don't build the rest on a weak core.
- **Sound is designed around actions:** the scuff on the frame a foot slips; thin the music
  when the clue / answer appears; check the final mix in mono and at low volume.
- **Rights & stems:** free, commercial-use, cross-platform-cleared assets only; record each
  asset's source + license + attribution; export dialogue / music / effects as separate stems.
- **Independent finish check:** transcribe the final mix (faster-whisper), check loudness +
  true peak, and re-watch the first minute, the hardest scene and the ending at phone size.
- **Research before scripting:** study ≥5 long-form comparisons on the channel (incl. a breakout
  vs a typical upload); log runtime, date, views@check-date, opening image, first payoff, one
  mid-turn and ending; write the ONE decision the comparison changed.
- **Delivery package per episode:** 1080p+ 16:9 MP4, English SRT, finished thumbnail, 2 alt
  title/thumbnail concepts, ready-to-paste title / description / chapters / credits / disclosure,
  editable timeline + stems, and a ZIP that rebuilds from a fresh directory. Keep source / temp /
  final in separate directories.
- **Shorts fall out of the long cut:** the single strongest ~45–60 s beat becomes the 9:16 teaser
  for IG + TikTok (full video stays on YouTube + Facebook). Teasers follow §1–2 and the
  short-form rules, and carry translated captions.
- **Platform:** never "made for kids"; add synthetic-media disclosure where a platform requires
  it; publishing / scheduling stays under moaz's control.

### Beyond Obvious — a reasonable prediction meets a real test (8–12 min)
- **Noodle** makes a prediction a smart viewer might share; **Pip** devises a test that could
  prove *either* of them wrong. Both are surprised at least once.
- Give the viewer a clear look at the **result before anyone explains it.**
- **Physics verification is the spine:** state assumptions, check units and a limiting case, and
  label on screen what is *measured* vs *simulated*. Run the calculation locally; save its data +
  figure **outside** the source directory.
- Structure refs: Practical Engineering "Automatic Bell Siphon" (clean demonstrable evidence),
  SmarterEveryDay "Backwards Brain Bicycle" (failed first attempts earn the payoff).

### Idiom Zoo — comedy that teaches English through consequences (7–10 min)
- **Kiki (parrot) & Bruno (dog)** — voices / standard from "Who Stole the Moon?". Fresh setting,
  a shared problem, conflicting plans.
- Pick **2–3 related expressions**; each must *change a decision*, cause a misunderstanding, or
  repair one. Check meaning / register / usage against a learner's dictionary.
- One joke an adult enjoys + one gag a learner follows **with the sound off.**
- Use a short original musical phrase once, then bring it back with a changed meaning or a comic
  interruption. End in a *different* everyday situation where the viewer has time to supply the
  expression.
- Structure refs: Simon's Cat "Missing Cat" (readable silent acting), RobWords phrase videos
  (a plausible mistake → curiosity). Give Kiki & Bruno their own jokes and timing.

### What If Lab — change one rule, follow one person (7–10 min)
- The channel's own cast: **Watt**, the lab's single curious mascot who runs the thought
  experiments (voice `af_bella`; the recurring **button gag** is a WL signature). Watt hosts; the
  experiment then follows **one** subject through the consequences. (Kiki & Bruno are Idiom Zoo's —
  never use them here.)
- State **one precise change** to the world and **label it as the fictional assumption.**
- Show an ordinary task **before** the change, replay it **after**, and let **one failed solution
  cause the next problem.** Track the same person / object / props through every attempt.
- **Verify the downstream physics**; separate robust consequences from uncertain ones.
  **End by returning to the opening task** so the change is unmistakable.
- Structure refs: xkcd "Drain the oceans" (one rule sustains a chain), Vsauce "Earth stopped
  spinning" (changes of scale).
