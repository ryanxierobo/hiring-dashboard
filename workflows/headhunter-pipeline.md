# Headhunter Automation Workflow v1.0

> **Owner:** Ryan Xie / Origami Robotics  
> **Last updated:** 2026-04-06  
> **Status:** Draft — iterate and improve

---

## Overview

Automated headhunter workflow that sources, researches, and pipelines candidates through a Kanban hiring board. The agent acts as a professional recruiter: finding candidates, enriching profiles with research, and advancing them through stages with documented notes at each step.

## Architecture

```
[Web Research] → [Profile Enrichment] → [HiringTool API] → [Pipeline Board]
     ↓                    ↓                     ↓                   ↓
  LinkedIn           Academic papers        add/move/update     Visual Kanban
  GitHub             Google Scholar         via JS evaluate     on localhost:8080
  Personal sites     YC/Company pages
```

**Dashboard:** `/private/tmp/hiring-dashboard/hiring.html` (served via `python3 -m http.server 8080`)  
**API:** `window.HiringTool` — full JS API exposed on the page  
**Browser control:** `openclaw browser evaluate --fn "..."` for API calls

---

## Pipeline Stages

| Stage | Owner | Purpose | Actions |
|-------|-------|---------|--------|
| **Qualified** | 🤖 Agent | Sourced & researched | Agent adds candidate with enriched profile |
| **Outreach Sent** | 🤖 Agent | Personalized message sent | Agent sends LinkedIn message after Ryan approves |
| **Responded** | 👤 Ryan | Candidate replied | Ryan moves here when they respond; signals interest |
| **Phone Screen** | 👤 Ryan | First call | Ryan conducts, logs notes |
| **Technical** | 👤 Ryan | Skills assessment | Technical interview |
| **Onsite** | 👤 Ryan | Team fit + deep dive | On-site evaluation |
| **Offer** | 👤 Ryan | Decision made | Offer details |
| **Hired** | 🎉 | Done | Onboarding |

### Workflow
1. **Agent** sources candidates → adds to **Qualified** column
2. **Ryan** reviews Qualified candidates → manually moves approved ones to **Outreach Sent**
3. **Agent** detects move → sends personalized LinkedIn outreach
4. If candidate responds → Ryan moves to **Responded**
5. From there, Ryan drives the interview process manually

## Workflow Steps

### Step 1: Source & Research

**Trigger:** User says "try with [name]" or "source [name/role]"

**Actions:**
1. Web search: `"[name]" [role] LinkedIn`
2. Web search: `"[name]" [domain] engineer robotics`
3. Fetch personal site / GitHub / Google Scholar
4. Extract: education, experience, publications, interests, links

**Research sources (priority order):**
- LinkedIn profile
- Personal website / portfolio
- GitHub (repos, contributions, languages)
- Google Scholar (papers, citations, h-index)
- YC directory (if applicable)
- Twitter/X (for culture fit signals)

**Output:** Structured candidate profile with sourcing notes.

### Step 2: Add to Pipeline

```javascript
HiringTool.add({
  name: 'Full Name',
  role: 'Target Role',
  email: 'email@example.com',
  source: 'YC Network',  // Referral|LinkedIn|AngelList|Inbound|YC Network|University|Other
  stage: 'Applied',
  flag: 'hot',           // hot|warm|cold
  notes: 'SOURCED: [key qualifications]. [education]. [experience]. [publications]. [links]'
});
```

**Flag criteria:**
- **Hot 🔥:** Direct domain match, top school/company, published researcher, referred by team
- **Warm 🟡:** Adjacent domain, solid background, needs more evaluation
- **Cold ⚪:** Speculative, early career, unclear fit

### Step 3: Outreach via LinkedIn (Applied → Phone Screen)

**LinkedIn Message Procedure (fixes for bugs 2-4):**

```bash
# 1. Navigate to profile (get the profileUrn for compose URL)
openclaw browser navigate "https://www.linkedin.com/in/[linkedin-slug]"

# 2. ALWAYS use --efficient for LinkedIn snapshots (Bug #4: full snapshot times out)
openclaw browser snapshot --efficient

# 3. Find the Message button — look for compose URL in the snapshot:
#    /messaging/compose/?profileUrn=urn%3Ali%3Afsd_profile%3A[ID]&recipient=[ID]
#    Click the "Message" link ref to open compose
openclaw browser click [message-ref]

# 4. Wait for compose box, then snapshot again
sleep 2 && openclaw browser snapshot --efficient

# 5. Type the message into the compose textbox
openclaw browser type [textbox-ref] "[message text]"

# 6. EXPLICITLY click the Send button (Bug #2: --submit does NOT work for LinkedIn)
#    Do NOT rely on --submit flag. Always find and click the Send button ref.
openclaw browser click [send-button-ref]

# 7. Screenshot to verify delivery
sleep 2 && openclaw browser screenshot
```

**⚠️ Known gotchas:**
- `--submit` flag does NOT press LinkedIn's Send button. Always click it explicitly.
- If candidate has prior message history, compose box is at bottom of thread. Use `snapshot --efficient` to find it.
- LinkedIn pages are huge. NEVER use full `snapshot` — always use `--efficient`.
- Alternative: use direct compose URL: `https://www.linkedin.com/messaging/compose/?recipient=[profileUrn]`

**Update pipeline after send:**
```javascript
HiringTool.move(candidateId, 'Phone Screen');
HiringTool.update(candidateId, {
  notes: existingNotes + '\n\n[OUTREACH YYYY-MM-DD] LinkedIn message sent. [personalized message summary]. [what we highlighted about their work]. Delivery confirmed.'
});
```

**Outreach template hooks:**
- Reference a specific paper/project they worked on
- Connect their research to Origami Robotics' mission
- Mention mutual YC connection if applicable
- Keep it short, specific, not generic

### Step 4: Phone Screen (Phone Screen → Technical)

```javascript
HiringTool.move(candidateId, 'Technical');
HiringTool.update(candidateId, {
  notes: existingNotes + '\n\n[PHONE SCREEN YYYY-MM-DD] [duration]. [communication quality]. [technical depth]. [culture fit signals]. [motivation]. VERDICT: [advance/hold/reject].'
});
```

**Evaluation criteria:**
- Communication clarity
- Technical depth in their domain
- Alignment with company mission
- Startup readiness (builder mindset vs. big-co comfort)
- Specific skills relevant to our stack

### Step 5: Technical (Technical → Onsite)

```javascript
HiringTool.move(candidateId, 'Onsite');
HiringTool.update(candidateId, {
  notes: existingNotes + '\n\n[TECHNICAL YYYY-MM-DD] [system design performance]. [coding assessment]. [domain-specific knowledge]. [hardware understanding if relevant]. VERDICT: [advance/hold/reject].'
});
```

### Step 6: Onsite → Offer → Hired

Same pattern — move + annotate at each stage.

---

## HiringTool API Reference

```javascript
// CRUD
HiringTool.add({ name, role, email?, source?, stage?, flag?, notes? })
HiringTool.get(id)
HiringTool.update(id, { ...fields })
HiringTool.remove(id)

// Pipeline
HiringTool.move(id, stageName)
HiringTool.advance(id)  // next stage

// Search & List
HiringTool.find(query)
HiringTool.list(stageName?)

// Analytics
HiringTool.stats()  // { total, byStage, bySource, byFlag, conversionRate }

// Bulk
HiringTool.bulk.add([...items])
HiringTool.bulk.move([...ids], stage)
HiringTool.bulk.advance([...ids])

// Data
HiringTool.export()
HiringTool.import(data)

// Command bar
HiringTool.exec("add Jane Doe as Engineer")
```

**Calling from agent:**
```bash
openclaw browser evaluate --fn "(function() { var c = HiringTool.add({...}); return JSON.stringify(c); })"
```

---

## Iteration Log

### v1.0 — 2026-04-06
- Initial workflow: manual web research → HiringTool API calls
- Tested with Quanting Xie (CMU Robotics PhD)
- Full pipeline: Applied → Phone Screen → Technical → Onsite
- Notes enriched at each stage with structured annotations

### v1.1 — 2026-04-06
- ✅ **Persistent localStorage** — candidates survive page refresh
- ✅ **LinkedIn outreach end-to-end** — browser navigates to profile, opens message compose, types personalized message, clicks Send
- ✅ **Full verification run** — sourced → added to board → LinkedIn message sent → delivery confirmed → board updated

### 🐛 Bugs Found During E2E Test
1. ✅ **FIXED: localStorage lost on code update** — killed old server at `/private/tmp/`, restarted serving from workspace clone which has persistence code. Server now runs from `/Users/ryan/.openclaw/workspace/hiring-dashboard/`.
2. ✅ **FIXED: `--submit` flag doesn't work for LinkedIn** — workflow now documents: always explicitly click the Send button ref. Never rely on `--submit`.
3. ✅ **FIXED: LinkedIn compose opens in existing thread** — workflow now uses `snapshot --efficient` to find compose box regardless of thread position. Also documented direct compose URL as alternative.
4. ✅ **FIXED: Snapshot timeout on heavy pages** — workflow now mandates `--efficient` flag for all LinkedIn snapshots. Never use full `snapshot` on LinkedIn.

### TODO for v1.2
- [x] **Serve updated HTML** — killed old server, now serving from workspace clone with persistence
- [x] **LinkedIn outreach procedure** — documented explicit Send button click, --efficient snapshots, compose URL
- [ ] **File-based persistence** — write candidates to `data/candidates.json` instead of localStorage
- [ ] **Outreach template system** — generate message from candidate research + configurable templates
- [ ] **Scoring rubric** — quantified evaluation (1-5) at each stage
- [ ] **Calendar integration** — auto-schedule interviews
- [ ] **Discord notifications** — alert team when candidate advances
- [ ] **Batch sourcing** — "find 10 robotics engineers" → bulk pipeline
- [ ] **Rejection tracking** — why candidates dropped, for pattern analysis

---

## Files

| File | Purpose |
|------|---------|
| `workflows/headhunter-pipeline.md` | This document — the workflow definition |
| `/private/tmp/hiring-dashboard/hiring.html` | The dashboard app (single HTML file) |
| `workflows/headhunter-templates/` | (future) Email templates, scoring rubrics |
| `workflows/headhunter-runs/` | (future) Logs of each sourcing run |

---

## How to Run

```
1. Agent receives: "source [name]" or "try with [name]"
2. Agent reads this workflow doc
3. Agent executes Steps 1-5 using web_search + web_fetch + browser evaluate
4. Agent reports results to user
5. User reviews board at localhost:8080
```

## How to Iterate

Edit this file! Change evaluation criteria, add new research sources, refine note templates, adjust flag thresholds. Each run improves the playbook.
