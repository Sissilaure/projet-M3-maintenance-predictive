from fastapi import APIRouter, HTTPException

from backend.app.services.training_service import train_all

router = APIRouter(tags=["training"])


@router.post("/train")
def train():
    try:
        return train_all()
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))