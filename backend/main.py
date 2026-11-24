
from fastapi import FastAPI
from pydantic import BaseModel

from backend.intent.analyzer import analyze_task
from backend.monitor.runtime_monitor import RuntimeMonitor
from backend.policy.policy_engine import PolicyEngine
from backend.execution.executor import ControlledExecutor
from backend.incidents.incident_reporter import IncidentReporter
from fastapi.middleware.cors import CORSMiddleware

from backend.database import (
    init_db,
    save_event,
    save_incident,
    get_events as get_saved_events,
    get_incidents as get_saved_incidents
)


app = FastAPI(title="ScopeGuard API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

monitor = RuntimeMonitor()
engine = PolicyEngine()
reporter = IncidentReporter()

policy = None
executor = None


class TaskRequest(BaseModel):
    task: str


class ActionRequest(BaseModel):
    action: str
    target: str
    content: str | None = None


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
def home():
    return {"message": "ScopeGuard API is running"}


@app.post("/task")
def create_task(request: TaskRequest):
    global policy, executor

    policy = analyze_task(request.task)
    executor = ControlledExecutor(policy, monitor, engine)

    return {
        "message": "Task registered",
        "policy": policy
    }


@app.post("/execute")
def execute_action(request: ActionRequest):

    if executor is None:
        return {"error": "Submit a task first"}

    result = executor.execute(
        request.action,
        request.target,
        request.content
    )

    event = monitor.get_events()[-1]

    # Save every activity event
    save_event(event)

    # Generate and save an incident if an action was blocked
    incident = reporter.report_incident(
        policy["task"],
        event,
        result
    )

    if incident is not None:
        save_incident(incident)

    return result


@app.get("/events")
def get_events():
    return get_saved_events()


@app.get("/incidents")
def get_incidents():
    return get_saved_incidents()

