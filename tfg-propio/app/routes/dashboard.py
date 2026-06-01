from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.dependencies import get_current_user
from app.models.crop import Crop
from app.models.planting_calendar import PlantingCalendar
from app.models.task import Task
from app.routes.planting_calendar import generate_calendar_events, is_calendar_complete
from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def is_pending(status: str | None) -> bool:
    return str(status or "").lower() not in {"completed", "done", "finalizada", "completada"}


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    current_user_id = current_user["user_id"]

    crops = db.query(Crop).options(
        joinedload(Crop.calendar),
    ).filter(Crop.user_id == current_user_id).order_by(Crop.id.desc()).all()

    tasks = db.query(Task).options(
        joinedload(Task.crops),
    ).filter(Task.user_id == current_user_id).order_by(Task.created_at.desc(), Task.id.desc()).all()

    pending_tasks = [task for task in tasks if is_pending(task.status)]
    active_calendars = []
    warnings = []

    for crop in crops:
        calendar = crop.calendar
        if calendar is None:
            warnings.append({
                "crop_id": crop.id,
                "crop_name": crop.name,
                "reason": "Sin fases configuradas",
            })
            continue

        if not is_calendar_complete(calendar):
            warnings.append({
                "crop_id": crop.id,
                "crop_name": crop.name,
                "reason": "Fases incompletas",
            })
            continue

        events = generate_calendar_events(calendar)
        if events:
            event = events[0]
            active_calendars.append({
                "crop_id": crop.id,
                "crop_name": crop.name,
                "phase": event.phase or "",
                "month": event.month,
                "half": event.half,
                "is_last_phase": event.is_last_phase,
            })
            if event.is_last_phase:
                warnings.append({
                    "crop_id": crop.id,
                    "crop_name": crop.name,
                    "reason": "Cultivo en la ultima fase",
                })

    return {
        "crops_count": len(crops),
        "active_calendar_count": len(active_calendars),
        "pending_tasks_count": len(pending_tasks),
        "overdue_tasks_count": 0,
        "incomplete_phase_crops_count": sum(
            1 for crop in crops if crop.calendar is None or not is_calendar_complete(crop.calendar)
        ),
        "pending_tasks": [
            {
                "id": task.id,
                "name": task.name,
                "description": task.description,
                "status": task.status,
                "crop_id": task.crop_id,
            }
            for task in pending_tasks[:5]
        ],
        "active_calendars": active_calendars[:6],
        "warnings": warnings[:6],
    }
