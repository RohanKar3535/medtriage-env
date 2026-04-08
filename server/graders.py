"""Deterministic graders for MedTriage-Env tasks.

All graders return scores strictly in (0, 0.95] to satisfy OpenEnv Phase 2
score_range validation. A perfect performance yields 0.95, not 1.0.
"""


def _clamp(score: float) -> float:
    """Clamp to (0.01, 0.95] — never exactly 0 or 1."""
    return round(min(max(score, 0.01), 0.95), 4)


def grade_single_triage(gold_esi: int, agent_esi: int) -> float:
    """
    Grade Task 1: Single patient ESI assignment.
    Exact match → 0.95, off-by-1 → 0.60, off-by-2 → 0.20, else → 0.05.
    """
    if agent_esi is None:
        return 0.01
    diff = abs(gold_esi - agent_esi)
    raw = {0: 0.95, 1: 0.60, 2: 0.20}.get(diff, 0.05)
    return _clamp(raw)


def kendall_tau(x: list, y: list) -> float:
    """
    Calculate Kendall's tau-b rank correlation coefficient.
    Pure Python implementation — no scipy dependency.
    Returns value in [-1, 1]. +1 = perfect agreement, -1 = reversed.
    """
    n = len(x)
    if n < 2:
        return 1.0

    concordant = 0
    discordant = 0
    for i in range(n):
        for j in range(i + 1, n):
            x_diff = x[i] - x[j]
            y_diff = y[i] - y[j]
            product = x_diff * y_diff
            if product > 0:
                concordant += 1
            elif product < 0:
                discordant += 1
            # ties (product == 0) are ignored

    total = concordant + discordant
    if total == 0:
        return 0.0
    return (concordant - discordant) / total


def grade_queue_ordering(
    agent_order: list,
    gold_order: list,
    agent_esi_assignments: dict,
    gold_esi_map: dict,
) -> float:
    """
    Grade Task 2: Queue ordering of 5 patients.
    Combined score: ordering quality (40%) + ESI accuracy (40%) + coverage (20%).
    """
    n = len(gold_order)
    if n == 0:
        return 0.01

    # --- Ordering component (Kendall's tau) ---
    if len(agent_order) < 2:
        tau_score = 0.0
    else:
        gold_rank = {pid: i for i, pid in enumerate(gold_order)}
        agent_ranks = []
        gold_ranks = []
        for i, pid in enumerate(agent_order):
            if pid in gold_rank:
                agent_ranks.append(i)
                gold_ranks.append(gold_rank[pid])

        if len(agent_ranks) < 2:
            tau_score = 0.0
        else:
            tau = kendall_tau(agent_ranks, gold_ranks)
            tau_score = (tau + 1.0) / 2.0  # normalize [-1,1] → [0,1]

    # --- ESI accuracy component ---
    esi_scores = []
    for pid, agent_esi in agent_esi_assignments.items():
        if pid in gold_esi_map:
            diff = abs(agent_esi - gold_esi_map[pid])
            esi_scores.append({0: 1.0, 1: 0.6, 2: 0.2}.get(diff, 0.0))

    avg_esi = sum(esi_scores) / len(esi_scores) if esi_scores else 0.0

    # --- Coverage component ---
    coverage = len(agent_order) / n

    # --- Combined ---
    score = 0.4 * tau_score + 0.4 * avg_esi + 0.2 * coverage
    return _clamp(score)


def grade_er_shift(
    survival_count: int,
    total_critical: int,
    discharged_count: int,
    total_patients: int,
    total_wait_minutes: float,
    num_waited: int,
    steps_taken: int,
    min_possible_steps: int,
) -> float:
    """
    Grade Task 3: Full ER shift management.
    Composite: survival (50%) + throughput (30%) + wait penalty (20%) × efficiency.
    """
    # Survival rate
    if total_critical > 0:
        survival_rate = survival_count / total_critical
    else:
        survival_rate = 1.0

    # Throughput
    throughput = discharged_count / total_patients if total_patients > 0 else 0.0

    # Average wait penalty
    if num_waited > 0:
        avg_wait = total_wait_minutes / num_waited
        wait_score = max(0.0, 1.0 - (avg_wait / 120.0))
    else:
        wait_score = 1.0

    # Efficiency bonus
    if min_possible_steps > 0:
        efficiency = max(0.0, 1.0 - max(0, steps_taken - min_possible_steps) * 0.02)
    else:
        efficiency = 1.0

    raw = survival_rate * 0.5 + throughput * 0.3 + wait_score * 0.2
    final = raw * efficiency
    return _clamp(final)
