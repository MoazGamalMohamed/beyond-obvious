# Viral Playbook — titles & first frames

Standing content rule for **all three brands** (Beyond Obvious, What If Lab, Idiom Zoo).
Every new episode must follow this for both the **on-platform title** (the first line of
its `caption`, and the YouTube title) and the **first frame / thumbnail** (the rendered
`cover_overlay`). Keep each brand's voice and characters separate — same *technique*, not
the same content.

> Origin: moaz compared our shorts to the viral ones in his feed
> (2026-11-28). Theirs pulled the eye; ours read like a textbook caption.

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
- Put the brand character **mid-action** in an intriguing situation
  (BO = NOODLE; WL and IZ = Kiki 🦜 & Bruno 🐶; in IZ, Bruno mid-way through taking the idiom literally).
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
  `src/episodes/epNNN_*.py` module (and the WL/IZ equivalents).
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
