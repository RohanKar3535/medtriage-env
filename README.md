---
title: MedTriage Env
emoji: 🏥
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
base_path: /web
---
# MedTriage-Env 🏥

**Emergency Department Patient Triage Environment for AI Agent Training**

An OpenEnv-compliant reinforcement learning environment where an AI agent acts as an Emergency Department (ED) triage nurse. The agent must assess patients using the **Emergency Severity Index (ESI)** 1–5 scale, order diagnostic tests, manage bed allocation, consult specialists, and handle patient deterioration — all under real-time constraints.

---

## Why This Domain?

Emergency triage is one of the most consequential time-pressure decisions in medicine. Every year, millions of patients are triaged in EDs worldwide. Getting triage wrong — over-triaging clogs critical beds; under-triaging delays life-saving care. Training AI agents to perform clinical triage is genuinely valuable for:

- **Agent evaluation**: Testing whether LLMs can reason about clinical urgency from natural language
- **RL research**: Multi-objective optimization (speed vs. accuracy vs. resource allocation)
- **Healthcare AI safety**: Understanding failure modes of AI clinical reasoning

---

## Environment Overview

| Property | Value |
|---|---|
| **Domain** | Emergency Department Triage |
| **API** | OpenEnv spec (`/reset`, `/step`, `/state`) |
| **Tasks** | 3 (easy → medium → hard) |
| **Patient Cases** | 50 clinically realistic synthetic cases |
| **Scoring** | Deterministic graders, 0.0–1.0 |
| **Reward** | Shaped (partial credit, penalties, efficiency bonus) |

---

## Tasks

### Task 1: `single_triage` (Easy)
- **Objective**: Assign ESI priority level to a single patient
- **Max Steps**: 5
- **Grading**: Exact ESI match → 0.95 | Off-by-1 → 0.60 | Off-by-2 → 0.20 | Else → 0.05
- **Expected Score**: ~0.60 for frontier models (requires clinical reasoning, not default guessing)

### Task 2: `queue_ordering` (Medium)
- **Objective**: Triage 5 patients in correct urgency order
- **Max Steps**: 15
- **Grading**: Kendall's τ rank correlation (40%) + ESI accuracy (40%) + coverage (20%)
- **Expected Score**: ~0.50+ for frontier models

### Task 3: `er_shift` (Hard)
- **Objective**: Manage a full 4-hour ER shift with 10 patients, limited beds, patient deterioration
- **Max Steps**: 40
- **Grading**: Survival rate (50%) × Throughput (30%) × Wait time (20%) × Efficiency bonus
- **Expected Score**: ~0.30+ for frontier models

---

## Action Space

| Action | Parameters | Description |
|---|---|---|
| `assign_priority` | `patient_id`, `esi_level` (1-5) | Assign ESI triage level |
| `order_test` | `patient_id`, `test_type` | Order diagnostic test |
| `admit_to_bed` | `patient_id` | Admit patient to available bed |
| `consult` | `patient_id`, `specialty` | Request specialist consult |
| `discharge` | `patient_id` | Discharge patient |
| `wait` | — | Wait (advances time in er_shift) |

**Valid tests**: `ECG`, `CBC`, `BMP`, `CT_head`, `CT_chest`, `X_ray`, `urinalysis`, `troponin`, `blood_culture`

**Valid specialties**: `cardiology`, `neurology`, `surgery`, `orthopedics`, `internal_medicine`, `pulmonology`, `psychiatry`

---

## Observation Space

Each observation includes:

| Field | Type | Description |
|---|---|---|
| `current_time` | int | Minutes into the shift |
| `bed_availability` | int | Number of free beds |
| `total_beds` | int | Total bed capacity (6) |
| `patients` | list | List of patient observations |
| `last_action_result` | str | Human-readable feedback |
| `last_reward` | float | Reward from previous action |
| `episode_step` | int | Current step number |
| `task_name` | str | Active task |
| `done` | bool | Whether episode is complete |

Each **patient** includes:

| Field | Type | Description |
|---|---|---|
| `patient_id` | str | Unique ID (e.g. P001) |
| `chief_complaint` | str | Natural language complaint |
| `vitals` | object | HR, BP, SpO2, Temp, RR |
| `age` | int | Patient age |
| `comorbidities` | list[str] | Pre-existing conditions |
| `wait_minutes` | int | Time waiting |
| `status` | str | waiting/triaged/admitted/discharged/deteriorated |
| `tests_completed` | list[str] | Completed tests |
| `assigned_esi` | int or null | Assigned ESI level |

---

## Reward Design

The reward function provides **shaped, non-sparse signal** at every step:

| Event | Reward | Rationale |
|---|---|---|
| Correct ESI assignment | +0.8 | Core task success |
| Close ESI (off by 1) | +0.3 | Partial credit |
| Appropriate test/consult | +0.2 | Clinical relevance |
| Critical patient admitted | +0.3 | Resource management |
| Patient discharged | +0.2 | Throughput |
| Unnecessary test/consult | +0.05 | Small reward, not optimal |
| Duplicate action | −0.2 to −0.3 | Penalize waste |
| Invalid action | −0.1 | Format/logic errors |
| Poor ESI (off by 3+) | −0.3 | Clinical danger |
| 3× repeated identical action | −1.0 + **episode terminates** | Anti-loop protection |
| Waiting (er_shift) | −0.05 | Patients deteriorate |

**Anti-loop protection**: After 3 identical consecutive actions, the episode terminates with score 0. This prevents agents from gaming rewards through repetition.

**Efficiency bonus**: `max(0, 1.0 - (steps_taken - min_steps) × 0.02)` — wasteful agents lose up to 100% of their score.

---

## Setup & Usage

### Docker (Recommended)

```bash
cd medtriage_env
docker build -t medtriage-env .
docker run --rm -p 7860:7860 medtriage-env
```

### Local Development

```bash
cd medtriage_env
pip install -r requirements.txt
uvicorn server.app:app --host 0.0.0.0 --port 7860
```

### Run Inference

```bash
export HF_TOKEN="your-token"
export ENV_URL="http://localhost:7860"
python inference.py
```

### Test Endpoints

```bash
# Health check
curl http://localhost:7860/health

# Reset to easy task
curl -X POST http://localhost:7860/reset -H "Content-Type: application/json" -d '{"task_name":"single_triage"}'

# Take an action
curl -X POST http://localhost:7860/step -H "Content-Type: application/json" -d '{"action_type":"assign_priority","patient_id":"P001","esi_level":2}'

# Get state
curl http://localhost:7860/state

# Get grade
curl http://localhost:7860/grade
```

---

## Baseline Scores

| Task | Score | Model |
|---|---|---|
| `single_triage` | ~0.60 | Qwen2.5-72B-Instruct |
| `queue_ordering` | ~0.55 | Qwen2.5-72B-Instruct |
| `er_shift` | ~0.38 | Qwen2.5-72B-Instruct |

---

## Project Structure

```
medtriage_env/
├── Dockerfile              # Container config (port 7860)
├── openenv.yaml            # OpenEnv metadata
├── inference.py            # Baseline inference script
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── server/
    ├── __init__.py
    ├── app.py              # FastAPI endpoints
    ├── env.py              # Environment state machine
    ├── models.py           # Pydantic typed models
    ├── graders.py          # Deterministic task graders
    └── patient_data.py     # 50 synthetic clinical cases
```

---

## OpenEnv Compliance

- ✅ Typed Pydantic models for Observation, Action, Reward
- ✅ `step()` → returns observation, reward, done, info
- ✅ `reset()` → returns initial observation
- ✅ `state()` → returns current state
- ✅ `openenv.yaml` with metadata
- ✅ 3 tasks with deterministic graders (easy → medium → hard)
- ✅ Scores in (0.01, 0.95] range — never boundary values
- ✅ Working Dockerfile
- ✅ Baseline inference script with reproducible scores
- ✅ Uses OpenAI client for LLM calls

---

## License

MIT
