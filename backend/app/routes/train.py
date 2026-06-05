from fastapi import APIRouter, HTTPException, BackgroundTasks
from datetime import datetime
from backend.app.services.training_service import train_all

router = APIRouter(tags=["training"])

# Training state tracking
_training_state = {
    "in_progress": False,
    "status": "idle",
    "progress": 0,
    "result": None,
    "error": None,
    "started_at": None,
    "completed_at": None,
}


def _reset_training_state():
    """Reset training state after completion."""
    global _training_state
    _training_state["in_progress"] = False
    _training_state["completed_at"] = datetime.now().isoformat()


def _run_training_sync():
    """Run training in background with state tracking."""
    global _training_state
    try:
        _training_state["in_progress"] = True
        _training_state["status"] = "loading_data"
        _training_state["progress"] = 10
        _training_state["started_at"] = datetime.now().isoformat()
        _training_state["error"] = None

        _training_state["status"] = "training_models"
        _training_state["progress"] = 50

        result = train_all()

        _training_state["status"] = "completed"
        _training_state["progress"] = 100
        _training_state["result"] = result
        _reset_training_state()
    except Exception as e:
        _training_state["status"] = "failed"
        _training_state["error"] = str(e)
        _training_state["in_progress"] = False
        _training_state["completed_at"] = datetime.now().isoformat()


@router.post("/train")
async def train(background_tasks: BackgroundTasks):
    """Start model training in background."""
    if _training_state["in_progress"]:
        raise HTTPException(
            status_code=409,
            detail="Un entraînement est déjà en cours. Attendez ou consultez /train/status"
        )

    background_tasks.add_task(_run_training_sync)
    return {
        "status": "started",
        "message": "Entraînement lancé en arrière-plan. Consultez /train/status pour le suivi.",
        "poll_interval_seconds": 2
    }


@router.get("/train/status")
def get_training_status():
    """Get current training status and progress."""
    return {
        "in_progress": _training_state["in_progress"],
        "status": _training_state["status"],
        "progress": _training_state["progress"],
        "started_at": _training_state["started_at"],
        "completed_at": _training_state["completed_at"],
        "result": _training_state["result"] if _training_state["status"] == "completed" else None,
        "error": _training_state["error"],
    }