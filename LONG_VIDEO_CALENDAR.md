# Long-Form Video Production Calendar

*One long-form episode per brand, built to the showrunner brief (`VIRAL_PLAYBOOK.md` §5).
Created 2026-11-28. Publishing stays under moaz's control — dates are production targets, not auto-publishes.*

## Context
The three flagship long-form videos (IZ "Who Stole the Moon?", BO "The Longer Track Won…",
WL "He Offered Free Toast…") shipped 2026-11-28, before this brief arrived. The episodes
below are the **first long-form videos produced to the brief** — one per brand, rotating
every two weeks, published on Saturdays for reach. Daily shorts continue in parallel (owned
by the daily content-ops task); each long video also spins off a ~60 s 9:16 teaser for
IG + TikTok, with the full cut on YouTube + Facebook and translated captions.

## Schedule at a glance
| Episode | Brand | Target publish (Sat) | Working title |
|---|---|---|---|
| BO-L2 | Beyond Obvious | 2026-12-12 | He Bet the Ice Would Melt on Wood First 🧊 |
| IZ-L2 | Idiom Zoo | 2026-12-26 | Bruno Said He Could "Wing It" on Live Radio 🎙️ |
| WL-L2 | What If Lab | 2027-01-09 | What If the Floor Lost All Friction for 60 Seconds? 🧁 |

Cadence continues after: BO ~Jan 23, IZ ~Feb 6, WL ~Feb 20 (one long video every ~2 weeks, rotating).

## Per-episode production timeline
(Hardest 30–45 s proven at release quality **first**, then the full render — per the brief.)

**BO-L2 — publish Sat Dec 12**
- Dec 2 — research (≥5 BO long comparisons) + premise lock + script
- Dec 6 — prove hardest 30–45 s (the measured side-by-side reveal + sound) at release quality
- Dec 7–10 — full render + edit; local physics calc → data + figure saved **outside** the source dir
- Dec 11 — finish checks (faster-whisper transcript, loudness/true-peak, phone-size review) + package + thumbnail & 2 alt concepts
- Dec 12 — publish (moaz) → 60 s teaser to IG/TikTok; translated captions follow

**IZ-L2 — publish Sat Dec 26**
- Dec 16 — research + 2–3 idioms locked (learner-dictionary checked) + script
- Dec 20 — prove hardest 30–45 s (sound-off gag lands + idiom clearly audible)
- Dec 21–24 — full render + edit
- Dec 25 — finish checks + package + thumbnail & 2 alt concepts
- Dec 26 — publish (moaz) → teaser + captions

**WL-L2 — publish Sat Jan 9**
- Dec 30 — research + the one world-rule locked + script
- Jan 3 — prove hardest 30–45 s (cold viewer follows cause→effect with narration muted)
- Jan 4–7 — full render + edit; downstream-physics check
- Jan 8 — finish checks + package + thumbnail & 2 alt concepts
- Jan 9 — publish (moaz) → teaser + captions

## Chosen premises

### BO-L2 — Beyond Obvious (8–12 min)
Reasonable prediction meets a real test, with physics verification.
- **Premise:** Identical ice cubes on a metal block and a wood block at the same starting
  temperature — which melts first, and why does *touching* the surfaces tempt you to bet the other way?
- **Noodle** predicts the wood melts it first ("metal feels freezing, it'll keep the ice frozen").
  **Pip** builds the side-by-side test. Both are surprised: the metal — which *felt* colder —
  melts the cube far faster.
- **Why (physics):** metal's high thermal conductivity/effusivity moves heat into the cube
  quickly; the *same* property makes it feel cold to the hand. Verify with a timed melt +
  surface thermometer (**measured**) and a 1-D heat-conduction simulation (**simulated**),
  labeled on screen; state assumptions, check units (W·m⁻¹·K⁻¹), test the insulator limiting
  case. Calc runs locally; data + figure saved outside the source directory.
- **First frame / thumbnail:** Noodle mid-reach between the two cubes, cover line "Which melts first?"
- **Opening shot:** Noodle touching both blocks, flinching at the "colder" metal.
- **Ending shot:** back to the two cubes — metal's is a puddle, wood's barely melted.
- **Send-to-a-friend moment:** the colder-*feeling* surface winning.
- **Alt titles:** "Cold Metal vs Warm Wood — Which Melts Ice? 🧊" · "He Touched Both and Guessed Wrong 🧊"

### IZ-L2 — Idiom Zoo (7–10 min)
Comedy that teaches English through consequences. Kiki (parrot) & Bruno (dog), voices/standard
from "Who Stole the Moon?".
- **Premise:** Bruno promises he can **"wing it"** hosting the community-radio hour. The ON AIR
  light comes on — and Kiki is the only one who prepared. Can Kiki **"buy him time"** without
  the listeners catching on?
- **Idioms (each must change a decision or cause/repair a misunderstanding):** *wing it*
  (Bruno's confidence), *buy (someone) time* (Kiki's rescue), *bite your tongue* (Kiki holding
  back from correcting him live). Checked against a learner's dictionary for meaning/register.
- **Jokes:** one line an adult enjoys; one visual gag (cue-card panic / stalling SFX) a learner
  follows with the sound off.
- **Music:** the station jingle used once, then returning with a changed meaning / comic interruption.
- **Ending:** a new everyday setting (Bruno about to "wing" ordering at a café) where the viewer
  has time to supply the idiom.
- **First frame / thumbnail:** Bruno confident at the mic, ON AIR glowing, Kiki panicking off-side;
  cover line "He didn't prepare…"
- **Send-to-a-friend moment:** the ON-AIR light snapping on with Bruno frozen.
- **Alt titles:** "The Only One Who Prepared Was the Parrot 🦜" · "Live Radio, Zero Prep — Can Kiki Save It? 🎙️"

### WL-L2 — What If Lab (7–10 min)
Change one rule, follow one person. Hosted by **Watt**, WL's single curious lab mascot (the
channel's established cast); the experiment follows one subject — a baker.
- **Premise:** A bakery floor loses **all** friction for one minute (walls + counter keep theirs).
  A baker has to deliver one cake across the room.
- **Rule (labeled fictional assumption):** μ_floor = 0 for 60 s; everything else normal.
- **Chain:** ordinary delivery before the change → after: walking fails (no traction) → the
  failed fix (running) spins the baker out → a workable solution emerges (push off a wall /
  throw-and-catch using momentum). Track the same baker, cake and shoes through every attempt.
- **Verify:** Newton's first law + conservation of momentum; separate **robust** consequences
  (can't walk, momentum carries you) from **uncertain** ones (exact spin / trajectory).
  **End by returning to the opening task** so the change is unmistakable.
- **First frame / thumbnail:** Watt presenting the rule, then the baker mid-slip with the cake
  flying; cover line "The floor stopped gripping"
- **Send-to-a-friend moment:** can the audience spot the workable solution before the baker does?
- **Alt titles:** "One Minute, No Friction — Can He Deliver the Cake? 🧁" · "The Floor Turned to Ice (Sort Of) 🧁"

## Tools (all free)
Existing render kit (`studio/concepts/render_kit/`) + `manim_fx/` for animated graphs/equations
(BO/WL) · FFmpeg/ffprobe for export checks · faster-whisper for the independent transcript ·
Blender / Shotcut / Kdenlive where an editable timeline helps. No paid tools.

## Notes
- **WL cast locked:** What If Lab's established character is **Watt**, the single curious lab
  mascot (from `brand2/WEEK1_PLAN.md` + `WIRING_PLAN.md` and the render brand kit `wif_brand.py`;
  voice `af_bella`, the "button" gag). Kiki & Bruno belong to **Idiom Zoo only** — never mix.
  The playbook has been corrected to match.
- Dates are production targets; publishing is yours to trigger.
