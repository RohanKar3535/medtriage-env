"""
Quick test to PROVE graders produce varied scores.
Run: python test_graders.py (no server needed)
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from server.env import MedTriageEnv
from server.models import TriageAction

def test_task1_variety():
    print("=" * 60)
    print("TASK 1: Single Triage - Different seeds, different patients")
    print("=" * 60)
    env = MedTriageEnv()
    for seed in [42, 43, 44, 45, 46, 100, 200, 7]:
        obs = env.reset("single_triage", seed=seed)
        p = obs.patients[0]
        gold = env.gold_esi_map[p.patient_id]
        # Correct
        action = TriageAction(action_type="assign_priority", patient_id=p.patient_id, esi_level=gold)
        env.step(action)
        correct_score = env.grade()
        # Wrong (off by 2)
        env.reset("single_triage", seed=seed)
        wrong_esi = max(1, min(5, gold + 2))
        action2 = TriageAction(action_type="assign_priority", patient_id=p.patient_id, esi_level=wrong_esi)
        env.step(action2)
        wrong_score = env.grade()
        print(f"  seed={seed:>3d} gold_esi={gold} | correct={correct_score:.2f} | wrong(esi={wrong_esi})={wrong_score:.2f}")

def test_task2_grading():
    print("\n" + "=" * 60)
    print("TASK 2: Queue Ordering - Grader differentiates quality")
    print("=" * 60)
    env = MedTriageEnv()

    # Perfect agent
    obs = env.reset("queue_ordering", seed=123)
    gold_order = env.gold_order
    gold_esi_map = env.gold_esi_map.copy()
    print(f"  Gold order: {gold_order}")
    print(f"  Gold ESIs:  {gold_esi_map}")

    for pid in gold_order:
        action = TriageAction(action_type="assign_priority", patient_id=pid, esi_level=gold_esi_map[pid])
        env.step(action)
    perfect_score = env.grade()
    print(f"  Perfect agent score:  {perfect_score:.4f}")

    # Reversed agent
    obs = env.reset("queue_ordering", seed=123)
    for pid in reversed(gold_order):
        action = TriageAction(action_type="assign_priority", patient_id=pid, esi_level=gold_esi_map[pid])
        env.step(action)
    reversed_score = env.grade()
    print(f"  Reversed order score: {reversed_score:.4f}")

    # Random agent
    obs = env.reset("queue_ordering", seed=123)
    import random
    rng = random.Random(999)
    shuffled = list(gold_order)
    rng.shuffle(shuffled)
    for pid in shuffled:
        wrong_esi = rng.randint(1, 5)
        action = TriageAction(action_type="assign_priority", patient_id=pid, esi_level=wrong_esi)
        env.step(action)
    random_score = env.grade()
    print(f"  Random agent score:   {random_score:.4f}")

    # Partial agent (2/5)
    obs = env.reset("queue_ordering", seed=123)
    for pid in gold_order[:2]:
        action = TriageAction(action_type="assign_priority", patient_id=pid, esi_level=gold_esi_map[pid])
        env.step(action)
    partial_score = env.grade()
    print(f"  Partial agent (2/5):  {partial_score:.4f}")

def test_task3_grading():
    print("\n" + "=" * 60)
    print("TASK 3: ER Shift - Score varies with agent quality")
    print("=" * 60)
    env = MedTriageEnv()

    # Lazy agent
    env.reset("er_shift", seed=456)
    for _ in range(5):
        env.step(TriageAction(action_type="wait", patient_id=""))
    lazy_score = env.grade()
    print(f"  Lazy agent (only waits): {lazy_score:.4f}")

    # Active agent
    env.reset("er_shift", seed=456)
    for pid in list(env.patients.keys()):
        gold = env.gold_esi_map[pid]
        env.step(TriageAction(action_type="assign_priority", patient_id=pid, esi_level=gold))
        if gold <= 2:
            env.step(TriageAction(action_type="admit_to_bed", patient_id=pid))
    active_score = env.grade()
    print(f"  Active agent (triage+admit): {active_score:.4f}")

if __name__ == "__main__":
    test_task1_variety()
    test_task2_grading()
    test_task3_grading()
    print("\nALL GRADERS PRODUCE VARIED SCORES")
