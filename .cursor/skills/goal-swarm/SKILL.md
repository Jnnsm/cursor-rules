---
name: goal-swarm
description: >-
  Four-role architecture swarm (Coder, UI/UX, Tester, PM) with cross-agent
  agreement and a hard verification gate before marking a goal complete. Use
  when delivering non-trivial features, multi-file work, UI changes, or any
  "get this done" goal; when agents might claim done without proof; or when
  the user mentions swarm, role agreement, or working-program guarantee.
---

# Goal swarm

Guarantee a working program by having four roles agree, then proving it with evidence.

## Roles

| Role | Owns | Must not |
|------|------|----------|
| **PM** | Goal clarity, scope, acceptance criteria, final sign-off | Implement or mark done without Tester evidence |
| **Coder** | Minimal correct implementation (ponytail), `AGENT_CHANGES.md` lines | Declare done; skip checks the Tester requires |
| **UI/UX** | User-facing clarity, layout/flow, a11y of surfaces touched | Invent UI when there is none; block on taste alone |
| **Tester** | Runnable verification plan and execution (`uv run prove`, tests, commands, file read-back) | Accept "it should work"; rubber-stamp without running checks |

## Spawn protocol

1. **PM first** — restate goal in one sentence + 3–7 acceptance criteria. Cut scope the user did not ask for (ponytail).
2. **Parallel design** — spawn **Coder** and **UI/UX** (UI/UX only if user-facing). Each proposes the smallest approach that meets acceptance.
3. **Disagree → resolve** — if proposals conflict: each names one concrete objection. PM picks the option that still meets acceptance with the smaller diff. Record the choice in the agreement block below.
4. **Coder implements** — only the agreed plan. No drive-by extras.
5. **Tester verifies** — runs the evidence commands; pastes output. Failures go back to Coder (one fix loop), then re-verify.
6. **PM signs off** — only after Tester evidence is green and roles agree.

Use Cursor Task/subagents for roles when available. If running solo, still **simulate the roles in order** and fill the agreement record — same gates apply.

## Agreement record (required before "done")

Copy and fill; leave blanks as fail:

```markdown
## Goal agreement
- Goal: …
- Acceptance: …
- Plan (chosen): …
- Dissent resolved: … | none
- Coder: AGREE | BLOCK — …
- UI/UX: AGREE | N/A | BLOCK — …
- Tester: AGREE | BLOCK — evidence: `…` (exit 0 / paths checked)
- PM: SIGN-OFF | HOLD — …
- Proof this session: `uv run prove` / other command output pasted
```

Any **BLOCK** or missing proof → not complete.

## Verification evidence (Tester)

Prefer, in order:

1. `uv run prove` → exit 0; paste full output.
2. Project tests / the command that proves the acceptance criteria.
3. File evidence: read the delivered paths and confirm required content exists.

Never: "tests would pass", "looks good", or unrun commands.

## Skip swarm (still keep the gate)

Trivia and explicit "skip swarm" still need **evidence before complete** when code or config changed: run prove/tests or show file proof. Q&A with no repo change needs no prove.
