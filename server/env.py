"""
MedTriage Environment — core state machine.

Implements reset(), step(), state(), and grade() for all three tasks:
  - single_triage  (easy)   : Assign ESI to 1 patient
  - queue_ordering (medium) : Triage 5 patients in correct urgency order
  - er_shift       (hard)   : Manage a full 4-hour ER shift with 10 patients
"""

import random
from copy import deepcopy
from typing import Dict, List, Optional, Tuple, Any

from .models import (
    VitalsModel,
    PatientObservation,
    EnvironmentObservation,
    TriageAction,
)
from .patient_data import CASE_LIBRARY, calculate_severity_score
from .graders import grade_single_triage, grade_queue_ordering, grade_er_shift


# ── Valid sets for input validation ──────────────────────────────
VALID_TESTS = {"ECG", "CBC", "BMP", "CT_head", "CT_chest", "X_ray",
               "urinalysis", "troponin", "blood_culture"}
VALID_SPECIALTIES = {"cardiology", "neurology", "surgery", "orthopedics",
                     "internal_medicine", "pulmonology", "psychiatry"}


class MedTriageEnv:
    """Emergency Department Triage Environment."""

    TASK_CONFIG = {
        "single_triage":  {"max_steps": 5,  "num_patients": 1,  "beds": 6, "time_step": 5},
        "queue_ordering": {"max_steps": 15, "num_patients": 5,  "beds": 6, "time_step": 5},
        "er_shift":       {"max_steps": 40, "num_patients": 10, "beds": 6, "time_step": 10},
    }

    DEFAULT_SEEDS = {"single_triage": 42, "queue_ordering": 123, "er_shift": 456}

    def __init__(self):
        self._reset_state()

    # ── internal helpers ─────────────────────────────────────────
    def _reset_state(self):
        self.task_name: str = "single_triage"
        self.seed: int = 42
        self.rng = random.Random(42)
        self.patients: Dict[str, dict] = {}
        self.triage_order: List[str] = []
        self.esi_assignments: Dict[str, int] = {}
        self.tests_ordered: Dict[str, List[str]] = {}
        self.consults_ordered: Dict[str, List[str]] = {}
        self.admitted: Dict[str, str] = {}
        self.discharged: set = set()
        self.deteriorated: set = set()
        self.current_time: int = 0
        self.total_beds: int = 6
        self.step_count: int = 0
        self.done: bool = False
        self.cumulative_reward: float = 0.0
        self.rewards: List[float] = []
        self.action_history: List[tuple] = []
        self.action_counter: Dict[tuple, int] = {}
        self.last_action_result: str = "Episode started. Review patients and take action."
        self.last_reward: float = 0.0
        self.pending_arrivals: List[Tuple[int, dict]] = []
        self.gold_order: List[str] = []
        self.gold_esi_map: Dict[str, int] = {}
        self.min_possible_steps: int = 1
        self._next_pid: int = 1
        self._next_bed: int = 1

    @property
    def config(self) -> dict:
        return self.TASK_CONFIG.get(self.task_name, self.TASK_CONFIG["single_triage"])

    @property
    def beds_free(self) -> int:
        return self.total_beds - len(self.admitted)

    # ── patient management ───────────────────────────────────────
    def _add_patient(self, case: dict, arrival_time: int = 0) -> str:
        pid = f"P{self._next_pid:03d}"
        self._next_pid += 1

        # Slight vitals randomisation (±5 %) for realism
        v = case["vitals"].copy()
        for k in v:
            val = v[k]
            if isinstance(val, (int, float)):
                delta = val * 0.05
                v[k] = type(val)(val + self.rng.uniform(-delta, delta))
        v["heart_rate"]       = max(0,  min(220, int(v["heart_rate"])))
        v["bp_systolic"]      = max(0,  min(260, int(v["bp_systolic"])))
        v["bp_diastolic"]     = max(0,  min(160, int(v["bp_diastolic"])))
        v["spo2"]             = max(0,  min(100, int(v["spo2"])))
        v["temperature"]      = round(max(94.0, min(108.0, float(v["temperature"]))), 1)
        v["respiratory_rate"] = max(0,  min(60,  int(v["respiratory_rate"])))

        self.patients[pid] = {
            "case": case,
            "vitals": v,
            "age": case.get("age", self.rng.randint(20, 80)),
            "arrival_time": arrival_time,
            "status": "waiting",
            "tests_completed": [],
            "consults_requested": [],
            "assigned_esi": None,
            "bed_id": None,
            "wait_triaged_at": None,
        }
        self.gold_esi_map[pid] = case["gold_esi"]
        return pid

    def _select_cases(self, esi_dist: Dict[int, int]) -> List[dict]:
        by_esi: Dict[int, list] = {}
        for c in CASE_LIBRARY:
            by_esi.setdefault(c["gold_esi"], []).append(c)
        out: list = []
        for esi, n in esi_dist.items():
            pool = by_esi.get(esi, [])
            if pool:
                out.extend(self.rng.sample(pool, min(n, len(pool))))
        self.rng.shuffle(out)
        return out

    # ── task setup ───────────────────────────────────────────────
    def _setup_single_triage(self):
        # Rotate ESI level by seed with offset so seed 42 avoids ESI-3
        # (LLMs default-guess ESI-3, making it trivially correct without the offset).
        # seed 42 → (42+3)%5=0 → ESI-1, seed 43 → ESI-2, seed 44 → ESI-3, ...
        esi_levels = [1, 2, 3, 4, 5]
        target_esi = esi_levels[(self.seed + 3) % len(esi_levels)]
        candidates = [c for c in CASE_LIBRARY if c["gold_esi"] == target_esi]
        if not candidates:
            candidates = CASE_LIBRARY
        case = self.rng.choice(candidates)
        self._add_patient(case)
        self.min_possible_steps = 1

    def _setup_queue_ordering(self):
        # Overlapping ESI levels make ordering ambiguous and harder
        # Two ESI-2s and two ESI-3s have close severity → LLM must read vitals
        cases = self._select_cases({1: 1, 2: 2, 3: 2})
        pids = [self._add_patient(c) for c in cases]
        scores = [
            (pid, calculate_severity_score(
                self.patients[pid]["case"],
                self.patients[pid]["vitals"],
                self.patients[pid]["age"],
            ))
            for pid in pids
        ]
        scores.sort(key=lambda x: -x[1])
        self.gold_order = [pid for pid, _ in scores]
        self.min_possible_steps = 5

    def _setup_er_shift(self):
        initial = self._select_cases({1: 1, 2: 1, 3: 1, 4: 1})
        for c in initial:
            self._add_patient(c, arrival_time=0)
        delayed = self._select_cases({2: 2, 3: 2, 4: 1, 5: 1})
        times = sorted(self.rng.sample(range(20, 200, 10), min(len(delayed), 6)))
        for c, t in zip(delayed, times):
            self.pending_arrivals.append((t, c))
        self.min_possible_steps = 4 + len(delayed)

    # ── public API ───────────────────────────────────────────────
    def reset(self, task_name: str = "single_triage", seed: Optional[int] = None) -> EnvironmentObservation:
        self._reset_state()
        self.task_name = task_name
        self.seed = seed if seed is not None else self.DEFAULT_SEEDS.get(task_name, 42)
        self.rng = random.Random(self.seed)
        self.total_beds = self.config["beds"]

        if task_name == "single_triage":
            self._setup_single_triage()
        elif task_name == "queue_ordering":
            self._setup_queue_ordering()
        elif task_name == "er_shift":
            self._setup_er_shift()
        else:
            raise ValueError(f"Unknown task: {task_name}")

        return self._get_observation()

    def step(self, action: TriageAction) -> Tuple[EnvironmentObservation, float, bool, dict]:
        if self.done:
            return self._get_observation(), 0.0, True, {"error": "Episode already done."}

        self.step_count += 1
        reward = 0.0
        info: Dict[str, Any] = {}

        # ── anti-loop: detect repeated identical actions ─────────
        action_key = (action.action_type, action.patient_id,
                      action.esi_level, action.test_type, action.specialty)
        self.action_history.append(action_key)
        self.action_counter[action_key] = self.action_counter.get(action_key, 0) + 1

        if self.action_counter[action_key] >= 3:
            self.done = True
            reward = -1.0
            self.last_action_result = (
                "EPISODE TERMINATED: Same action repeated 3 times. "
                "Repeating the same action is penalized."
            )
            self.last_reward = reward
            self.cumulative_reward += reward
            self.rewards.append(reward)
            return self._get_observation(), reward, True, {"error": "repeated_actions"}

        # ── handle action by type ────────────────────────────────
        at = action.action_type

        if at == "assign_priority":
            reward, msg = self._handle_assign_priority(action)
        elif at == "order_test":
            reward, msg = self._handle_order_test(action)
        elif at == "admit_to_bed":
            reward, msg = self._handle_admit(action)
        elif at == "consult":
            reward, msg = self._handle_consult(action)
        elif at == "discharge":
            reward, msg = self._handle_discharge(action)
        elif at == "wait":
            reward, msg = self._handle_wait()
        else:
            reward, msg = -0.1, f"Invalid action type: {at}"

        self.last_action_result = msg
        self.last_reward = reward
        self.cumulative_reward += reward
        self.rewards.append(reward)

        # ── advance time (er_shift) ──────────────────────────────
        if self.task_name == "er_shift":
            self.current_time += self.config["time_step"]
            self._process_arrivals()
            self._process_deterioration()

        # ── check episode end ────────────────────────────────────
        self._check_done()

        return self._get_observation(), reward, self.done, info

    def state(self) -> dict:
        return {
            "task_name": self.task_name,
            "seed": self.seed,
            "step_count": self.step_count,
            "current_time": self.current_time,
            "done": self.done,
            "cumulative_reward": round(self.cumulative_reward, 4),
            "rewards": [round(r, 4) for r in self.rewards],
            "beds_free": self.beds_free,
            "patients_total": len(self.patients),
            "patients_triaged": len(self.triage_order),
            "patients_admitted": len(self.admitted),
            "patients_discharged": len(self.discharged),
            "patients_deteriorated": len(self.deteriorated),
        }

    def grade(self) -> float:
        if self.task_name == "single_triage":
            pid = list(self.patients.keys())[0] if self.patients else None
            if pid and pid in self.esi_assignments:
                gold = self.gold_esi_map[pid]
                agent = self.esi_assignments[pid]
                score = grade_single_triage(gold, agent)
                self._grade_detail = {
                    "patient_id": pid, "gold_esi": gold,
                    "agent_esi": agent, "diff": abs(gold - agent),
                    "score": round(score, 4),
                }
                return score
            self._grade_detail = {"error": "no_assignment"}
            return 0.01

        elif self.task_name == "queue_ordering":
            score = grade_queue_ordering(
                self.triage_order, self.gold_order,
                self.esi_assignments, self.gold_esi_map,
            )
            self._grade_detail = {
                "agent_order": self.triage_order,
                "gold_order": self.gold_order,
                "agent_esi": dict(self.esi_assignments),
                "gold_esi": dict(self.gold_esi_map),
                "score": round(score, 4),
            }
            return score

        elif self.task_name == "er_shift":
            critical_pids = [
                pid for pid, data in self.patients.items()
                if data["case"]["gold_esi"] <= 2
            ]
            survived = sum(
                1 for pid in critical_pids if pid not in self.deteriorated
            )
            total_wait = 0.0
            n_waited = 0
            for pid, data in self.patients.items():
                wt = data.get("wait_triaged_at")
                if wt is not None:
                    total_wait += wt - data["arrival_time"]
                    n_waited += 1

            return grade_er_shift(
                survived, len(critical_pids),
                len(self.discharged), len(self.patients),
                total_wait, n_waited,
                self.step_count, self.min_possible_steps,
            )
        return 0.01

    # ── action handlers ──────────────────────────────────────────
    def _handle_assign_priority(self, action: TriageAction) -> Tuple[float, str]:
        pid = action.patient_id
        if pid not in self.patients:
            return -0.1, f"Patient {pid} does not exist."
        if action.esi_level is None:
            return -0.1, "esi_level is required for assign_priority."
        if pid in self.esi_assignments:
            return -0.3, f"Patient {pid} already triaged (ESI {self.esi_assignments[pid]}). Duplicate assignment penalized."

        gold = self.gold_esi_map[pid]
        diff = abs(gold - action.esi_level)
        self.esi_assignments[pid] = action.esi_level
        self.triage_order.append(pid)
        self.patients[pid]["assigned_esi"] = action.esi_level
        self.patients[pid]["status"] = "triaged"
        self.patients[pid]["wait_triaged_at"] = self.current_time

        if diff == 0:
            return 0.8, f"Correct! Patient {pid} triaged ESI-{action.esi_level} (gold ESI-{gold})."
        elif diff == 1:
            return 0.3, f"Close. Patient {pid} triaged ESI-{action.esi_level}, gold was ESI-{gold} (off by 1)."
        elif diff == 2:
            return 0.0, f"Patient {pid} triaged ESI-{action.esi_level}, gold was ESI-{gold} (off by 2)."
        else:
            return -0.3, f"Poor triage. Patient {pid} assigned ESI-{action.esi_level}, gold was ESI-{gold} (off by {diff})."

    def _handle_order_test(self, action: TriageAction) -> Tuple[float, str]:
        pid = action.patient_id
        if pid not in self.patients:
            return -0.1, f"Patient {pid} does not exist."
        if not action.test_type:
            return -0.1, "test_type is required for order_test."
        if action.test_type not in VALID_TESTS:
            return -0.1, f"Invalid test: {action.test_type}. Valid: {', '.join(sorted(VALID_TESTS))}"

        existing = self.tests_ordered.setdefault(pid, [])
        if action.test_type in existing:
            return -0.2, f"Test {action.test_type} already ordered for {pid}."

        existing.append(action.test_type)
        self.patients[pid]["tests_completed"].append(action.test_type)

        required = self.patients[pid]["case"].get("required_tests", [])
        if action.test_type in required:
            return 0.2, f"Appropriate test {action.test_type} ordered for {pid}."
        else:
            return 0.05, f"Test {action.test_type} ordered for {pid} (not clinically indicated)."

    def _handle_admit(self, action: TriageAction) -> Tuple[float, str]:
        pid = action.patient_id
        if pid not in self.patients:
            return -0.1, f"Patient {pid} does not exist."
        if pid in self.admitted:
            return -0.2, f"Patient {pid} already admitted to bed {self.admitted[pid]}."
        if self.beds_free <= 0:
            return -0.1, f"No beds available ({self.total_beds}/{self.total_beds} occupied)."
        if pid not in self.esi_assignments:
            return -0.1, f"Patient {pid} must be triaged before admission."

        bed_id = f"B{self._next_bed:02d}"
        self._next_bed += 1
        self.admitted[pid] = bed_id
        self.patients[pid]["bed_id"] = bed_id
        self.patients[pid]["status"] = "admitted"

        esi = self.esi_assignments.get(pid, 5)
        if esi <= 2:
            return 0.3, f"Critical patient {pid} admitted to {bed_id}. Good."
        elif esi == 3:
            return 0.15, f"Patient {pid} admitted to {bed_id}."
        else:
            return 0.05, f"Patient {pid} (ESI-{esi}) admitted to {bed_id}. Low-acuity patients may not need beds."

    def _handle_consult(self, action: TriageAction) -> Tuple[float, str]:
        pid = action.patient_id
        if pid not in self.patients:
            return -0.1, f"Patient {pid} does not exist."
        if not action.specialty:
            return -0.1, "specialty is required for consult."
        if action.specialty not in VALID_SPECIALTIES:
            return -0.1, f"Invalid specialty: {action.specialty}. Valid: {', '.join(sorted(VALID_SPECIALTIES))}"

        existing = self.consults_ordered.setdefault(pid, [])
        if action.specialty in existing:
            return -0.2, f"Consult {action.specialty} already requested for {pid}."

        existing.append(action.specialty)
        self.patients[pid]["consults_requested"].append(action.specialty)

        required = self.patients[pid]["case"].get("required_consults", [])
        if action.specialty in required:
            return 0.2, f"Appropriate consult {action.specialty} for {pid}."
        else:
            return 0.05, f"Consult {action.specialty} for {pid} (may not be needed)."

    def _handle_discharge(self, action: TriageAction) -> Tuple[float, str]:
        pid = action.patient_id
        if pid not in self.patients:
            return -0.1, f"Patient {pid} does not exist."
        if pid in self.discharged:
            return -0.2, f"Patient {pid} already discharged."
        if pid not in self.esi_assignments:
            return -0.2, f"Cannot discharge {pid} — not yet triaged."

        # Check admission BEFORE freeing the bed
        was_admitted = pid in self.admitted

        # Free bed if admitted
        if was_admitted:
            del self.admitted[pid]
        self.discharged.add(pid)
        self.patients[pid]["status"] = "discharged"

        esi = self.gold_esi_map.get(pid, 5)
        if esi <= 2 and not was_admitted:
            return -0.3, f"Warning: discharging critical patient {pid} (ESI-{esi}) without admission."
        return 0.2, f"Patient {pid} discharged successfully."

    def _handle_wait(self) -> Tuple[float, str]:
        # Waiting costs time; patients may deteriorate
        if self.task_name == "er_shift":
            return -0.05, "Waited. Time advanced. Patients may be deteriorating."
        return 0.0, "Waited."

    # ── time & deterioration (er_shift) ──────────────────────────
    def _process_arrivals(self):
        arrived = []
        remaining = []
        for t, case in self.pending_arrivals:
            if self.current_time >= t:
                pid = self._add_patient(case, arrival_time=t)
                arrived.append(pid)
            else:
                remaining.append((t, case))
        self.pending_arrivals = remaining
        if arrived:
            self.last_action_result += f" New arrivals: {', '.join(arrived)}."

    def _process_deterioration(self):
        for pid, data in self.patients.items():
            if pid in self.deteriorated or pid in self.discharged:
                continue
            if data["status"] in ("admitted",):
                continue  # admitted patients are being cared for
            thresh = data["case"].get("deterioration_threshold")
            if thresh is None:
                continue
            wait_time = self.current_time - data["arrival_time"]
            if wait_time >= thresh and pid not in self.esi_assignments:
                self.deteriorated.add(pid)
                data["status"] = "deteriorated"
                self.last_action_result += (
                    f" ALERT: Patient {pid} deteriorated after {wait_time}min wait!"
                )

    def _check_done(self):
        cfg = self.config
        if self.step_count >= cfg["max_steps"]:
            self.done = True
            return

        if self.task_name == "single_triage":
            if self.triage_order:
                self.done = True

        elif self.task_name == "queue_ordering":
            if len(self.triage_order) >= len(self.patients):
                self.done = True

        elif self.task_name == "er_shift":
            if self.current_time >= 240:
                self.done = True
            all_handled = all(
                pid in self.discharged or pid in self.deteriorated
                for pid in self.patients
            )
            if all_handled and not self.pending_arrivals:
                self.done = True

    # ── observation building ─────────────────────────────────────
    def _get_observation(self) -> EnvironmentObservation:
        patient_obs = []
        for pid, data in self.patients.items():
            v = data["vitals"]
            patient_obs.append(PatientObservation(
                patient_id=pid,
                chief_complaint=data["case"]["chief_complaint"],
                vitals=VitalsModel(**v),
                age=data["age"],
                comorbidities=data["case"].get("comorbidities", []),
                arrival_time=data["arrival_time"],
                wait_minutes=max(0, self.current_time - data["arrival_time"]),
                status=data["status"],
                tests_completed=data["tests_completed"],
                consults_requested=data["consults_requested"],
                assigned_esi=data["assigned_esi"],
                bed_id=data["bed_id"],
            ))

        return EnvironmentObservation(
            current_time=self.current_time,
            bed_availability=self.beds_free,
            total_beds=self.total_beds,
            patients=patient_obs,
            last_action_result=self.last_action_result,
            last_reward=round(self.last_reward, 4),
            episode_step=self.step_count,
            task_name=self.task_name,
            done=self.done,
        )


# Singleton for the FastAPI app
env = MedTriageEnv()
