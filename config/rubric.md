# Scoring Rubric v3 (final — derived from validated questionnaire, 2026-07-20)

Do not modify weights without an explicit "recalibrate" session with the user.

## Gates (pass/fail — excluded silently, never shown in digest)

1. Company is on the approved watchlist.
2. Level band: Senior PM / PM II–III equivalent. Reject Director+, Head-of, VP, APM/entry,
   and roles requiring 10+ yrs.
3. Location: any India city or India-hybrid passes. **Remote-only is out.**
   Non-Bengaluru India roles pass but carry a `[NON-BLR]` flag (see checklist addendum).
4. Posting age < 45 days.
5. Rhythm gate: company (or the specific org) notorious for bad WLB → excluded entirely.
   Watchlist `rhythm_verdict: fail` enforces this; `unknown` passes but lands on the checklist.
6. Stability gate (startups only): no visible ≥24–36 months runway (recent raise, healthy
   headcount trajectory) → excluded.

## Scores (total 100)

| # | Dimension | Pts | Layer | Notes |
|---|---|---|---|---|
| 1 | Mission & problem hardness | 25 | Role | Decomposed: defined hard problem (10) · user research & experimentation core to the role (8) · end-to-end build proximity — talk to users, incorporate, ship (7) |
| 2 | Depth of AI work in the role | 15 | Role | Decomposed: frontier-relevant work — agents, evals, LLM systems the market hires for (8) · **skill portability** — transfers across companies vs. proprietary-stack knowledge (7) |
| 3 | Talent density | 15 | Company | Leadership caliber, where PMs come from / exit to, a lead worth learning from |
| 4 | Operating rhythm (above the gate) | 15 | Company | Gate removes the notorious; points reward *famously humane* over *standard pace* |
| 5 | Stability & distribution power | 15 | Company | Scaled/big-tech or well-funded; distribution not a struggle (user's F2/F3 answers) |
| 6 | Scope / surface ownership | 10 | Role | Full surface > fragments, but demoted per questionnaire |
| 7 | Company AI-nativeness | 5 | Company | Low weight by design: role-level AI depth matters more; post-AI-transformation scaled cos are fine |

Dropped (0 pts, validated): moat compounding (voice/vernacular) · GPM trajectory legibility.

## Thresholds & digest

- ≥70 → shortlist (appears in digest). ≥80 → outreach draft attached (two variants).
- Digest cap 25/week, sorted by score; note truncation. Typical expected volume <15.
- Nothing below 70 or gated is ever shown. Silence means nothing qualified.

## Research checklist (attach to every shortlisted role — fields for AYUSHI to fill)

- [ ] Rhythm verification: ≤9h/day typical · ≤2–3 weekend stretches/quarter · hours flexible
      within the day. (Ask: "Tell me about the last time a major project slipped — what
      happened to the people on it?")
- [ ] Runway / funding facts (startups): last raise, months of runway, burn signals.
- [ ] Manager quality + team peers: who is the lead, would she learn from them?
- [ ] Culture screens (verbatim): "Who was promoted into product leadership in the last year,
      and from where?" · "What does the exec team disagree about right now?"
- [ ] Comp: **hard floor fixed ≥ ₹55 LPA** (cash only; ESOP/variable = discounted paper).
      **Decision benchmark: total ≥ ₹90 LPA**, or a written reason why this role justifies less.
- [ ] `[NON-BLR]` addendum: comp floor holds AFTER relocation math · move survives the
      marriage-timeline conversation.

## Calibration anchors (ground truth — user's own scores of real pipeline roles)

- Decagon, first PM Duet: 85
- Talabat, Qcommerce Hub: 75
- Ember AI, Technical PM: 70
- Razorpay, Sr PM Growth SME Payments: 60
- Angel One, Sr PM AI personalization: 50

On "recalibrate": re-score these five; flag any drift >±7 points.

## Standing quarterly check (every 13 weeks)

Open the digest with: "Are you more hireable at your dream companies than you were last
quarter? What relevant AI skill did you add?" Track `last_quarterly_check` in state meta.
