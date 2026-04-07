"""
MedTriage-Env — Baseline Inference Script
==========================================
Runs an LLM agent against all 3 tasks and logs [START]/[STEP]/[END] to stdout.

Required env vars:
  API_BASE_URL   LLM endpoint  (default: HF router)
  MODEL_NAME     Model id      (default: Qwen/Qwen2.5-72B-Instruct)
  HF_TOKEN       API key
  ENV_URL        Running env URL (default: http://localhost:7860)
"""

import json
import os
import sys
import textwrap
import time
from typing import List, Optional

import requests
from openai import OpenAI

# ── configuration ────────────────────────────────────────────────
API_KEY = os.getenv("HF_TOKEN") or os.getenv("API_KEY") or ""
API_BASE_URL = os.getenv("API_BASE_URL", "https://router.huggingface.co/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")
ENV_URL = os.getenv("ENV_URL", "http://localhost:7860")
BENCHMARK = "medtriage_env"
TEMPERATURE = 0.3
MAX_TOKENS = 300

TASKS = [
    {"name": "single_triage", "max_steps": 5},
    {"name": "queue_ordering", "max_steps": 15},
    {"name": "er_shift",       "max_steps": 40},
]

SYSTEM_PROMPT = textwrap.dedent("""\
You are an experienced emergency department triage nurse using the Emergency Severity Index (ESI) 1-5 scale.

ESI LEVELS:
- ESI-1 (Resuscitation): Immediately life-threatening. Cardiac arrest, respiratory failure, major trauma.
- ESI-2 (Emergent): High risk, severe pain, altered mental status. Chest pain/MI, stroke, overdose, GI bleed.
- ESI-3 (Urgent): Requires 2+ resources. Abdominal pain, fractures, pneumonia, kidney stones.
- ESI-4 (Less Urgent): Requires 1 resource. Simple lacerations, sprains, UTI, earache.
- ESI-5 (Non-Urgent): No resources needed. Cold, prescription refill, minor rash, follow-up.

AVAILABLE ACTIONS (respond with exactly ONE valid JSON object):
1. {"action_type":"assign_priority","patient_id":"P001","esi_level":2}
2. {"action_type":"order_test","patient_id":"P001","test_type":"ECG"}
   Valid tests: ECG, CBC, BMP, CT_head, CT_chest, X_ray, urinalysis, troponin, blood_culture
3. {"action_type":"admit_to_bed","patient_id":"P001"}
4. {"action_type":"consult","patient_id":"P001","specialty":"cardiology"}
   Valid specialties: cardiology, neurology, surgery, orthopedics, internal_medicine, pulmonology, psychiatry
5. {"action_type":"discharge","patient_id":"P001"}
6. {"action_type":"wait","patient_id":""}

STRATEGY:
- Triage the MOST URGENT patients first (lowest ESI number).
- Look at vitals: low SpO2, high HR, low BP, high fever = more urgent.
- Look at chief complaint for life-threatening keywords.
- For Task 1: Assign ESI to the single patient.
- For Task 2: Triage all 5 patients, starting with the most critical.
- For Task 3: Triage, order tests, admit critical patients, consult specialists, then discharge.
- NEVER repeat the same action. Each action should make progress.

Respond with ONLY a single JSON object. No explanation, no markdown, no extra text.
""").strip()


# ── logging helpers ──────────────────────────────────────────────
def log_start(task: str, env: str, model: str):
    print(f"[START] task={task} env={env} model={model}", flush=True)

def log_step(step: int, action: str, reward: float, done: bool, error: Optional[str]):
    e = error if error else "null"
    print(f"[STEP] step={step} action={action} reward={reward:.2f} done={str(done).lower()} error={e}", flush=True)

def log_end(success: bool, steps: int, score: float, rewards: List[float]):
    rs = ",".join(f"{r:.2f}" for r in rewards)
    print(f"[END] success={str(success).lower()} steps={steps} score={score:.3f} rewards={rs}", flush=True)


# ── env helpers ──────────────────────────────────────────────────
def env_reset(task_name: str) -> dict:
    r = requests.post(f"{ENV_URL}/reset", json={"task_name": task_name}, timeout=30)
    r.raise_for_status()
    return r.json()

def env_step(action: dict) -> dict:
    r = requests.post(f"{ENV_URL}/step", json=action, timeout=30)
    r.raise_for_status()
    return r.json()

def env_grade() -> float:
    r = requests.get(f"{ENV_URL}/grade", timeout=10)
    r.raise_for_status()
    return r.json().get("score", 0.0)


# ── LLM call ─────────────────────────────────────────────────────
def build_user_prompt(obs: dict, step_num: int) -> str:
    patients_info = ""
    for p in obs.get("patients", []):
        v = p.get("vitals", {})
        patients_info += (
            f"\n  [{p['patient_id']}] Status: {p['status']} | Age: {p['age']} | "
            f"ESI assigned: {p.get('assigned_esi', 'none')}\n"
            f"    Complaint: {p['chief_complaint']}\n"
            f"    Vitals: HR={v.get('heart_rate')}, BP={v.get('bp_systolic')}/{v.get('bp_diastolic')}, "
            f"SpO2={v.get('spo2')}%, Temp={v.get('temperature')}°F, RR={v.get('respiratory_rate')}\n"
            f"    Comorbidities: {', '.join(p.get('comorbidities', [])) or 'none'}\n"
            f"    Wait: {p.get('wait_minutes', 0)}min | Tests: {p.get('tests_completed', [])} | "
            f"Consults: {p.get('consults_requested', [])} | Bed: {p.get('bed_id', 'none')}\n"
        )

    return textwrap.dedent(f"""\
Step {step_num} | Task: {obs.get('task_name')} | Time: {obs.get('current_time')}min
Beds: {obs.get('bed_availability')}/{obs.get('total_beds')} available
Last action result: {obs.get('last_action_result')}
Last reward: {obs.get('last_reward', 0)}

PATIENTS:{patients_info}
Choose your next action. Respond with ONLY valid JSON.""")


def get_llm_action(client: OpenAI, obs: dict, step_num: int) -> dict:
    prompt = build_user_prompt(obs, step_num)
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            stream=False,
        )
        text = (resp.choices[0].message.content or "").strip()

        # Strip markdown fences if present
        if text.startswith("```"):
            lines = text.split("\n")
            lines = [l for l in lines if not l.startswith("```")]
            text = "\n".join(lines).strip()

        action = json.loads(text)
        return action
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from text
        try:
            start = text.index("{")
            end = text.rindex("}") + 1
            return json.loads(text[start:end])
        except Exception:
            pass
        # Ultimate fallback
        patients = obs.get("patients", [])
        if patients:
            for p in patients:
                if p.get("assigned_esi") is None:
                    return {"action_type": "assign_priority", "patient_id": p["patient_id"], "esi_level": 3}
        return {"action_type": "wait", "patient_id": ""}
    except Exception as e:
        print(f"[DEBUG] LLM error: {e}", flush=True)
        return {"action_type": "wait", "patient_id": ""}


# ── main loop ────────────────────────────────────────────────────
def run_task(client: OpenAI, task_name: str, max_steps: int) -> float:
    rewards: List[float] = []
    steps_taken = 0
    score = 0.0
    success = False

    log_start(task=task_name, env=BENCHMARK, model=MODEL_NAME)

    try:
        obs = env_reset(task_name)
        done = obs.get("done", False)

        for step in range(1, max_steps + 1):
            if done:
                break

            action = get_llm_action(client, obs, step)
            action_str = json.dumps(action, separators=(",", ":"))

            result = env_step(action)
            obs = result.get("observation", {})
            reward = result.get("reward", 0.0)
            done = result.get("done", False)
            error = result.get("info", {}).get("error")

            rewards.append(reward)
            steps_taken = step

            # Shorten action string for log
            short_action = f"{action.get('action_type','?')}({action.get('patient_id','')}"
            if action.get("esi_level"):
                short_action += f",esi={action['esi_level']}"
            if action.get("test_type"):
                short_action += f",{action['test_type']}"
            if action.get("specialty"):
                short_action += f",{action['specialty']}"
            short_action += ")"

            log_step(step=step, action=short_action, reward=reward, done=done, error=error)

            if done:
                break

        score = env_grade()
        success = score >= 0.3

    except Exception as e:
        print(f"[DEBUG] Task {task_name} error: {e}", flush=True)
    finally:
        log_end(success=success, steps=steps_taken, score=score, rewards=rewards)

    return score


def main():
    if not API_KEY:
        print("[DEBUG] WARNING: No API key found. Set HF_TOKEN or API_KEY.", flush=True)

    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)

    # Wait for env to be ready
    for attempt in range(10):
        try:
            r = requests.get(f"{ENV_URL}/health", timeout=5)
            if r.status_code == 200:
                break
        except Exception:
            pass
        print(f"[DEBUG] Waiting for env... attempt {attempt + 1}", flush=True)
        time.sleep(2)

    scores = {}
    for task in TASKS:
        scores[task["name"]] = run_task(client, task["name"], task["max_steps"])

    print(f"\n[SUMMARY] Scores: {scores}", flush=True)
    print(f"[SUMMARY] Average: {sum(scores.values()) / len(scores):.3f}", flush=True)


if __name__ == "__main__":
    main()
