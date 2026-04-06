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

| Stage | Purpose | Agent Actions |
|-------|---------|---------------|
| **Applied** | Initial sourcing | Web research, profile enrichment, add candidate |
| **Phone Screen** | First contact | Send personalized outreach, log response |
| **Technical** | Skills assessment | Evaluate technical depth, log findings |
| **Onsite** | Team fit + deep dive | Comprehensive evaluation notes |
| **Offer** | Decision made | Compensation research, offer details |
| **Hired** | Done | Onboarding notes |

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

### Step 3: Outreach (Applied → Phone Screen)

```javascript
HiringTool.move(candidateId, 'Phone Screen');
HiringTool.update(candidateId, {
  notes: existingNotes + '\n\n[OUTREACH YYYY-MM-DD] [personalized message summary]. [what we highlighted about their work]. [connection to our mission].'
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
1. **localStorage lost on code update** — when serving from `/private/tmp/`, the seed data runs fresh. Need to either (a) serve the updated HTML with persistence, or (b) persist to a JSON file instead of localStorage so it survives across server restarts.
2. **`--submit` flag on `openclaw browser type` doesn't auto-press Enter for LinkedIn** — had to click Send button separately. Workflow should always explicitly click the Send button.
3. **LinkedIn message compose opens in existing thread** — if there's prior conversation history, the compose box is at the bottom of a long chat. Need to scroll to it or use the compose URL directly.
4. **Snapshot timeout on heavy pages** — LinkedIn profile page is massive; `--efficient` flag is essential. Full snapshot can timeout.

### TODO for v1.2
- [ ] **Serve updated HTML** — kill old server, restart with new persistent version
- [ ] **File-based persistence** — write candidates to `data/candidates.json` instead of localStorage
- [ ] **Outreach template system** — generate message from candidate research + configurable templates
- [ ] **Scoring rubric** — quantified evaluation (1-5) at each stage
- [ ] **Calendar integration** — auto-schedule interviews
- [ ] **Slack/Discord notifications** — alert team when candidate advances
- [ ] **Batch sourcing** — "find 10 robotics engineers" → bulk pipeline
- [ ] **Rejection tracking** — why candidates dropped, for pattern analysis
- [ ] **Email templates** — per-stage outreach templates with variable substitution
- [ ] **Competitor tracking** — flag if candidate is interviewing elsewhere
- [ ] **LinkedIn compose via direct URL** — use `/messaging/compose/?recipient=...` URL to avoid thread scrolling issues

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
