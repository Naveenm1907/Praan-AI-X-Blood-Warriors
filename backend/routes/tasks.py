from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db
from database.models import Donor as DonorDB  # SQLAlchemy model
from models.task import Task
from models.patient import Patient
from models.donor import Donor  # Pydantic model
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["tasks"])


class AssignRequest(BaseModel):
    warrior_id: int


class UpdateDonorRequest(BaseModel):
    donor_id: str
    response: str


@router.get("/warrior")
def get_warrior_tasks(
    date: str = Query(None, description="Filter by date (YYYY-MM-DD). Defaults to today."),
    status: str = Query(None, description="Filter by status: pending, in_progress, completed, failed"),
    db: Session = Depends(get_db)
):
    """
    Get tasks for Blood Warrior app.
    Returns tasks with patient info enriched.
    """
    query = db.query(Task)

    # Filter by date
    if date:
        try:
            filter_date = datetime.strptime(date, "%Y-%m-%d")
            query = query.filter(
                Task.created_at >= filter_date,
                Task.created_at < filter_date.replace(hour=23, minute=59, second=59)
            )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Filter by status
    if status:
        query = query.filter(Task.status == status)
    else:
        # Default: only pending/in_progress
        query = query.filter(Task.status.in_(["pending", "in_progress"]))

    tasks = query.order_by(
        # Urgency order: CRITICAL > URGENT > SOON > SCHEDULED
        Task.urgency == "CRITICAL",
        Task.urgency == "URGENT",
        Task.urgency == "SOON",
        Task.created_at.desc()
    ).all()

    # Enrich with patient data
    result = []
    for task in tasks:
        patient = db.query(Patient).filter(Patient.id == task.patient_id).first()
        task_dict = task.to_dict()
        if patient:
            task_dict["patient_name"] = patient.name
            task_dict["patient_age"] = patient.age
            task_dict["patient_blood_group"] = patient.blood_group
            task_dict["patient_phone"] = patient.phone
            task_dict["patient_location"] = patient.location
            task_dict["patient_severity"] = patient.severity
            task_dict["days_until_transfusion"] = patient.days_until_transfusion
        result.append(task_dict)

    return result


@router.get("/{task_id}")
def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    """Get detailed task info with patient data"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    patient = db.query(Patient).filter(Patient.id == task.patient_id).first()
    task_dict = task.to_dict()

    if patient:
        task_dict["patient_name"] = patient.name
        task_dict["patient_age"] = patient.age
        task_dict["patient_blood_group"] = patient.blood_group
        task_dict["patient_phone"] = patient.phone
        task_dict["patient_location"] = patient.location
        task_dict["patient_severity"] = patient.severity
        task_dict["patient_severity_score"] = patient.severity_score
        task_dict["days_until_transfusion"] = patient.days_until_transfusion
        task_dict["next_transfusion_date"] = patient.next_transfusion_date

    # Enrich assigned_donors with real phone numbers from database
    assigned_donors = task_dict.get("assigned_donors") or []
    if assigned_donors:
        donor_ids = [d["donor_id"] for d in assigned_donors]
        donors = db.query(DonorDB).filter(DonorDB.id.in_(donor_ids)).all()
        donor_map = {d.id: d for d in donors}
        for donor in assigned_donors:
            real_donor = donor_map.get(donor["donor_id"])
            if real_donor:
                donor["phone"] = real_donor.phone
                donor["name"] = real_donor.name

    return task_dict


@router.post("/{task_id}/assign")
def assign_task_to_warrior(
    task_id: int,
    body: AssignRequest,
    db: Session = Depends(get_db)
):
    """Assign task to specific warrior"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.warrior_id = body.warrior_id
    task.status = "in_progress"
    db.commit()

    return {"status": "success", "message": f"Task {task_id} assigned to warrior {body.warrior_id}"}


@router.post("/{task_id}/update-donor")
def update_donor_response(
    task_id: int,
    body: UpdateDonorRequest,
    db: Session = Depends(get_db)
):
    """
    Update donor response in task.
    response: confirmed, declined, no_answer, not_contacted
    """
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update donor in assigned_donors
    assigned_donors = task.assigned_donors or []
    for donor in assigned_donors:
        if donor["donor_id"] == body.donor_id:
            donor["contacted"] = True
            donor["response"] = body.response
            break

    task.assigned_donors = assigned_donors
    db.commit()

    return {"status": "success", "message": f"Donor {body.donor_id} response updated"}


@router.post("/{task_id}/complete")
def complete_task(task_id: int, db: Session = Depends(get_db)):
    """Mark task as completed"""
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = "completed"
    task.completed_at = datetime.now()
    db.commit()

    # Count confirmed donors
    assigned_donors = task.assigned_donors or []
    confirmed = sum(1 for d in assigned_donors if d.get("response") == "confirmed")

    return {
        "status": "success",
        "message": f"Task {task_id} completed",
        "confirmed_donors": confirmed,
        "total_donors": len(assigned_donors),
    }


@router.get("/stats/summary")
def get_task_stats(db: Session = Depends(get_db)):
    """Get task statistics"""
    total = db.query(Task).count()
    pending = db.query(Task).filter(Task.status == "pending").count()
    in_progress = db.query(Task).filter(Task.status == "in_progress").count()
    completed = db.query(Task).filter(Task.status == "completed").count()
    failed = db.query(Task).filter(Task.status == "failed").count()

    # Today's tasks
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_tasks = db.query(Task).filter(Task.created_at >= today_start).count()

    return {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "failed": failed,
        "today": today_tasks,
    }
