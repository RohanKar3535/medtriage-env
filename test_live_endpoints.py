"""
End-to-end live test against running server (port 7860).
Proves graders produce varied, legitimate scores for different agent qualities.
"""
import requests
import json
import random

BASE = "http://localhost:7860"

def post(path, data=None):
    r = requests.post(f"{BASE}{path}", json=data or {}, timeout=10)
    r.raise_for_status()
    return r.json()

def get(path):
    r = requests.get(f"{BASE}{path}", timeout=10)
    r.raise_for_status()
    return r.json()

# ── Test 1: Health + Root ────────────────────────────────────────
print("=" * 60)
print("ENDPOINT TESTS")
print("=" * 60)
health = get("/health")
print(f"  /health  -> {health}")
assert health["status"] == "healthy", "Health check failed!"

root = get("/")
print(f"  /        -> {root['environment']}")

tasks = get("/tasks")
print(f"  /tasks   -> {[t['name'] for t in tasks['tasks']]}")

# ── Test 2: Task 1 — Correct Agent ──────────────────────────────
print("\n" + "=" * 60)
print("TASK 1: SINGLE TRIAGE - Correct vs Wrong vs Random")
print("=" * 60)

# Correct agent
obs = post("/reset", {"task_name": "single_triage", "seed": 42})
pid = obs["patients"][0]["patient_id"]
state = get("/state")
# We need to figure out gold ESI — seed 42 -> ESI-1
result = post("/step", {"action_type": "assign_priority", "patient_id": pid, "esi_level": 1})
grade = get("/grade")
correct_score = grade["score"]
print(f"  Correct (ESI=1): score={correct_score}, detail={grade.get('detail', {})}")

# Wrong agent (off by 2)
obs = post("/reset", {"task_name": "single_triage", "seed": 42})
pid = obs["patients"][0]["patient_id"]
result = post("/step", {"action_type": "assign_priority", "patient_id": pid, "esi_level": 3})
grade = get("/grade")
wrong_score = grade["score"]
print(f"  Wrong   (ESI=3): score={wrong_score}, detail={grade.get('detail', {})}")

# Really wrong agent (off by 3+)
obs = post("/reset", {"task_name": "single_triage", "seed": 45})  # (45+3)%5=3 -> ESI-4
pid = obs["patients"][0]["patient_id"]
result = post("/step", {"action_type": "assign_priority", "patient_id": pid, "esi_level": 1})
grade = get("/grade")
terrible_score = grade["score"]
print(f"  Terrible(ESI=1, gold=4): score={terrible_score}, detail={grade.get('detail', {})}")


assert correct_score > wrong_score, f"Correct ({correct_score}) should beat wrong ({wrong_score})!"
assert wrong_score > terrible_score or wrong_score == terrible_score, "Scores should decrease with error!"
print("  [OK] Task 1 grader differentiates agent quality!")

# ── Test 3: Task 2 — Perfect vs Reversed vs Partial ─────────────
print("\n" + "=" * 60)
print("TASK 2: QUEUE ORDERING - Perfect vs Reversed vs Partial")
print("=" * 60)

# Perfect agent — triage all in correct order with correct ESIs
# We first need to discover the gold order by looking at state
obs = post("/reset", {"task_name": "queue_ordering", "seed": 123})
patients = obs["patients"]
pids = [p["patient_id"] for p in patients]
state = get("/state")

# We don't know gold ESIs via the API, so let's try ESI-2 for all
# (some will be right, some wrong — the point is testing variation)
print(f"  Patients: {pids}")

# Agent A: Assign all ESI-2 in order
obs = post("/reset", {"task_name": "queue_ordering", "seed": 123})
for p in obs["patients"]:
    post("/step", {"action_type": "assign_priority", "patient_id": p["patient_id"], "esi_level": 2})
grade_a = get("/grade")
score_a = grade_a["score"]
print(f"  All ESI-2:     score={score_a}")

# Agent B: Assign all ESI-5 (wrong) in order
obs = post("/reset", {"task_name": "queue_ordering", "seed": 123})
for p in obs["patients"]:
    post("/step", {"action_type": "assign_priority", "patient_id": p["patient_id"], "esi_level": 5})
grade_b = get("/grade")
score_b = grade_b["score"]
print(f"  All ESI-5:     score={score_b}")

# Agent C: Only triage 2 out of 5
obs = post("/reset", {"task_name": "queue_ordering", "seed": 123})
for p in obs["patients"][:2]:
    post("/step", {"action_type": "assign_priority", "patient_id": p["patient_id"], "esi_level": 3})
grade_c = get("/grade")
score_c = grade_c["score"]
print(f"  Partial (2/5): score={score_c}")

# Agent D: Random ESIs
obs = post("/reset", {"task_name": "queue_ordering", "seed": 123})
rng = random.Random(999)
for p in obs["patients"]:
    post("/step", {"action_type": "assign_priority", "patient_id": p["patient_id"], "esi_level": rng.randint(1, 5)})
grade_d = get("/grade")
score_d = grade_d["score"]
print(f"  Random ESIs:   score={score_d}")

scores_t2 = {score_a, score_b, score_c, score_d}
assert len(scores_t2) > 1, "Task 2 grader returned same score for all agents!"
print(f"  [OK] Task 2 grader produces {len(scores_t2)} distinct scores!")

# ── Test 4: Task 3 — Lazy vs Active ─────────────────────────────
print("\n" + "=" * 60)
print("TASK 3: ER SHIFT - Lazy vs Active")
print("=" * 60)

# Lazy agent (just waits)
obs = post("/reset", {"task_name": "er_shift", "seed": 456})
for _ in range(5):
    result = post("/step", {"action_type": "wait", "patient_id": ""})
grade_lazy = get("/grade")
print(f"  Lazy agent:   score={grade_lazy['score']}")

# Active agent (triages everyone)
obs = post("/reset", {"task_name": "er_shift", "seed": 456})
for p in obs["patients"]:
    post("/step", {"action_type": "assign_priority", "patient_id": p["patient_id"], "esi_level": 2})
    post("/step", {"action_type": "admit_to_bed", "patient_id": p["patient_id"]})
grade_active = get("/grade")
print(f"  Active agent: score={grade_active['score']}")

# ── Test 5: Anti-loop protection ─────────────────────────────────
print("\n" + "=" * 60)
print("ANTI-LOOP PROTECTION TEST")
print("=" * 60)
obs = post("/reset", {"task_name": "er_shift", "seed": 456})
for i in range(4):
    result = post("/step", {"action_type": "wait", "patient_id": ""})
    print(f"  wait #{i+1}: done={result['done']}, reward={result['reward']}")
    if result["done"]:
        break

# -- Test 6: No assignment -> score 0
print("\n" + "=" * 60)
print("NO ACTION TEST - Task 1 without triage")
print("=" * 60)
obs = post("/reset", {"task_name": "single_triage", "seed": 42})
# Don't triage, just grade
grade_none = get("/grade")
print(f"  No triage: score={grade_none['score']}, detail={grade_none.get('detail', {})}")
assert grade_none["score"] == 0.0, "Score should be 0 when no triage done!"
print("  [OK] No triage = score 0.0!")

print("\n" + "=" * 60)
print("ALL LIVE ENDPOINT TESTS PASSED [OK]")
print("=" * 60)
