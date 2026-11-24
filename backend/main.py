
from fastapi import FastAPI
from pydantic import BaseModel

from backend.intent.analyzer import analyze_task
from backend.monitor.runtime_monitor import RuntimeMonitor
from backend.policy.policy_engine import PolicyEngine
from backend.execution.executor import ControlledExecutor
from backend.incidents.incident_reporter import IncidentReporter


app = FastAPI(title="ScopeGuard API")

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


@app.get("/")
def home():
    return {"message": "ScopeGuard API is running"}


@app.post("/task")
def create_task(request: TaskRequest):
    global policy, executor

    policy = analyze_task(request.task)
    executor = ControlledExecutor(policy, monitor, engine)

    return {"message": "Task registered", "policy": policy}


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

    reporter.report_incident(
        policy["task"],
        event,
        result
    )

    return result


@app.get("/events")
def get_events():
    return monitor.get_events()


@app.get("/incidents")
def get_incidents():
    return reporter.get_incidents()

