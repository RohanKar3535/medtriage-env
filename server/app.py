"""FastAPI server for MedTriage-Env — OpenEnv compliant."""

from fastapi import FastAPI, Request
from typing import Optional

from .models import (
    TriageAction,
    EnvironmentObservation,
    StepResponse,
    ResetRequest,
)
from .env import env

app = FastAPI(
    title="MedTriage-Env",
    description="Emergency Department Triage OpenEnv Environment",
    version="1.0.0",
)


@app.get("/")
def root():
    return {
        "status": "ok",
        "environment": "medtriage-env",
        "version": "1.0.0",
        "description": "Emergency Department Triage Environment for RL agent training",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "service": "medtriage-env"}


@app.post("/reset")
async def reset_env(request: Request):
    try:
        body = await request.json()
    except Exception:
        body = {}
        
    task_name = body.get("task_name", "single_triage")
    seed = body.get("seed", None)
    
    obs = env.reset(task_name=task_name, seed=seed)
    return obs.model_dump()


@app.post("/step")
async def step_env(action: TriageAction):
    obs, reward, done, info = env.step(action)
    return StepResponse(
        observation=obs, reward=round(reward, 4), done=done, info=info
    ).model_dump()


@app.get("/state")
async def get_state():
    return env.state()


@app.get("/grade")
async def get_grade():
    score = env.grade()
    detail = getattr(env, "_grade_detail", {})
    return {"score": round(score, 4), "task": env.task_name, "detail": detail}


@app.get("/metrics")
def get_metrics():
    return {
        "tasks_completed": [env.step_count],
        "average_score": env.grade(),
        "grader_version": "1.0.0"
    }


@app.get("/tasks")
async def get_tasks():
    return {
        "tasks": [
            {
                "name": "single_triage",
                "difficulty": "easy",
                "description": "Assign ESI priority level to a single patient.",
                "max_steps": 5,
            },
            {
                "name": "queue_ordering",
                "difficulty": "medium",
                "description": "Triage 5 patients in correct urgency order.",
                "max_steps": 15,
            },
            {
                "name": "er_shift",
                "difficulty": "hard",
                "description": "Manage a full 4-hour ER shift: triage, test, admit, consult, and discharge 10 patients under resource constraints.",
                "max_steps": 40,
            },
            {
                "name": "mass_casualty",
                "difficulty": "hard",
                "description": "15 patients arrive in waves, only 4 beds. Agent must triage and immediately discharge low-acuity patients to free beds for critical ones.",
                "max_steps": 50,
            },
        ],
        "action_types": [
            "assign_priority", "order_test", "admit_to_bed",
            "consult", "discharge", "wait",
        ],
    }


def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=7860)


if __name__ == "__main__":
    main()
