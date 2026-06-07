"""
Autonomous AI Agent - Acts like a human coordinator
Daily cycle: Find urgent patients → Rank donors → Create tasks → Start campaigns
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.patient import Patient
from models.task import Task, AgentRun
from engine.match import rank_donors
from routes.donor import load_donors_from_db, load_donors_from_json
from routes.workflow import workflows_db
import uuid
import logging

logger = logging.getLogger(__name__)


class PRAANAgent:
    """Autonomous coordinator that runs daily cycles"""

    def __init__(self, db: Session):
        self.db = db

    def run_daily_cycle(self, auto_contact: bool = False) -> dict:
        """
        Main daily cycle:
        1. Find urgent patients (transfusion within 7 days)
        2. For each patient, AI rank donors
        3. Create workflow + warrior tasks
        4. Optionally auto-start contact campaigns
        5. Generate report
        """
        run_start = datetime.now()
        report = {
            "run_time": run_start.isoformat(),
            "urgent_patients": [],
            "workflows_created": [],
            "tasks_created": [],
            "campaigns_started": [],
        }

        # Step 1: Find urgent patients
        urgent_patients = self._find_urgent_patients(days_threshold=7)
        logger.info(f"Agent found {len(urgent_patients)} urgent patients")

        for patient in urgent_patients:
            try:
                # Step 2: Create workflow
                workflow_id = self._create_workflow(patient)
                report["workflows_created"].append(workflow_id)

                # Step 3: AI rank donors and assign top 10
                ranked_donors = self._ai_rank_donors(patient)
                self._assign_donors_to_workflow(workflow_id, ranked_donors[:10])

                # Step 4: Create warrior task
                task = self._create_warrior_task(patient, ranked_donors[:10])
                report["tasks_created"].append(task.id)

                # Step 5: Optionally auto-start campaigns
                if auto_contact and len(ranked_donors) > 0:
                    campaign_id = self._auto_start_campaign(workflow_id)
                    report["campaigns_started"].append(campaign_id)

                report["urgent_patients"].append({
                    "patient_id": patient.id,
                    "name": patient.name,
                    "urgency": patient.urgency_level,
                    "blood_group": patient.blood_group,
                    "donors_assigned": min(10, len(ranked_donors)),
                })

            except Exception as e:
                logger.error(f"Failed to process patient {patient.id}: {e}")
                report["urgent_patients"].append({
                    "patient_id": patient.id,
                    "name": patient.name,
                    "error": str(e),
                })

        # Log agent run
        agent_run = AgentRun(
            run_date=run_start,
            patients_processed=len(urgent_patients),
            workflows_created=len(report["workflows_created"]),
            tasks_created=len(report["tasks_created"]),
            campaigns_started=len(report["campaigns_started"]),
            status="success" if len(report["urgent_patients"]) == len(urgent_patients) else "partial",
            report=report,
        )
        self.db.add(agent_run)
        self.db.commit()

        logger.info(f"Agent cycle complete: {len(urgent_patients)} patients, {len(report['tasks_created'])} tasks")
        return report

    def _find_urgent_patients(self, days_threshold: int = 7) -> list:
        """Find patients who need transfusion within threshold days"""
        cutoff_date = (datetime.now() + timedelta(days=days_threshold)).strftime('%Y-%m-%d')

        patients = self.db.query(Patient).filter(
            Patient.is_active == True,
            (
                (Patient.urgency_level.in_(['CRITICAL', 'URGENT', 'SOON'])) |
                (Patient.days_until_transfusion <= days_threshold)
            )
        ).all()

        # Sort by urgency (CRITICAL first)
        urgency_order = {'CRITICAL': 0, 'URGENT': 1, 'SOON': 2, 'SCHEDULED': 3}
        patients.sort(key=lambda p: urgency_order.get(p.urgency_level, 99))

        return patients

    def _create_workflow(self, patient: Patient) -> str:
        """Create workflow for patient"""
        wid = f"wf{uuid.uuid4().hex[:8]}"

        workflow = {
            "workflow_id": wid,
            "patient_id": str(patient.id),
            "patient_data": {
                "patient_id": str(patient.id),
                "name": patient.name,
                "blood_group": patient.blood_group,
                "latitude": 17.385,  # Default Hyderabad coords
                "longitude": 78.4867,
                "urgency": patient.urgency_level or "SCHEDULED",
            },
            "current_step": "patient_registered",
            "steps": [
                {
                    "step_name": "Patient Registered",
                    "status": "completed",
                    "started_at": datetime.now().isoformat(),
                    "completed_at": datetime.now().isoformat(),
                    "details": f"Blood group: {patient.blood_group}, Urgency: {patient.urgency_level}",
                },
                {
                    "step_name": "AI Donor Matching",
                    "status": "in_progress",
                    "started_at": datetime.now().isoformat(),
                    "details": "Running XGBoost model to predict donor response probability"
                },
                {"step_name": "WhatsApp Campaign", "status": "pending"},
                {"step_name": "Voice Call Campaign", "status": "pending"},
                {"step_name": "Donors Confirmed", "status": "pending"},
            ],
            "scoring_method": "xgboost_ai",
            "created_at": datetime.now().isoformat(),
            "completed_at": None,
        }

        workflows_db[wid] = workflow
        return wid

    def _ai_rank_donors(self, patient: Patient) -> list:
        """AI-powered donor ranking for patient"""
        try:
            donors = load_donors_from_db(self.db)
            if not donors:
                donors = load_donors_from_json()
        except Exception:
            donors = load_donors_from_json()

        # Use patient location (default to Hyderabad if not set)
        latitude = 17.385
        longitude = 78.4867

        ranked = rank_donors(
            donors,
            patient.blood_group,
            latitude,
            longitude,
            count=20
        )

        return ranked

    def _assign_donors_to_workflow(self, workflow_id: str, donors: list):
        """Assign ranked donors to workflow"""
        if workflow_id in workflows_db:
            workflows_db[workflow_id]["ranked_donors"] = donors
            workflows_db[workflow_id]["current_step"] = "donors_ranked"
            workflows_db[workflow_id]["steps"][1]["status"] = "completed"
            workflows_db[workflow_id]["steps"][1]["completed_at"] = datetime.now().isoformat()
            workflows_db[workflow_id]["steps"][1]["details"] = f"Assigned {len(donors)} donors"

    def _create_warrior_task(self, patient: Patient, assigned_donors: list) -> Task:
        """Create task for Blood Warrior"""
        donor_data = [
            {
                "donor_id": d.get("donor_id"),
                "name": d.get("name"),
                "score": d.get("readiness_score"),
                "contacted": False,
                "response": None,
            }
            for d in assigned_donors
        ]

        task = Task(
            patient_id=patient.id,
            warrior_id=None,  # Unassigned, warrior self-assigns
            assigned_donors=donor_data,
            urgency=patient.urgency_level or "SCHEDULED",
            status="pending",
        )
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def _auto_start_campaign(self, workflow_id: str) -> str:
        """Auto-start voice campaign for workflow"""
        workflow = workflows_db.get(workflow_id)
        if not workflow or not workflow.get("ranked_donors"):
            return None

        campaign_id = f"vc{uuid.uuid4().hex[:6]}"

        # Simulate starting voice calls to top 5 donors
        call_results = []
        for donor in workflow["ranked_donors"][:5]:
            call_results.append({
                "donor_id": donor.get("donor_id"),
                "name": donor.get("name"),
                "phone": donor.get("phone", "+91 99999-00000"),
                "status": "call_initiated",
                "initiated_at": datetime.now().isoformat(),
                "readiness_score": donor.get("readiness_score"),
            })

        workflow["voice_campaign"] = call_results
        workflow["current_step"] = "voice_calls_initiated"
        workflow["steps"][3]["status"] = "in_progress"
        workflow["steps"][3]["started_at"] = datetime.now().isoformat()
        workflow["steps"][3]["details"] = f"Auto-started: {len(call_results)} voice calls"

        return campaign_id

    def get_last_run_status(self) -> dict:
        """Get status of last agent run"""
        last_run = self.db.query(AgentRun).order_by(AgentRun.created_at.desc()).first()
        if not last_run:
            return {"status": "never_run", "message": "Agent has not been run yet"}

        return last_run.to_dict()

    def get_todays_tasks(self) -> list:
        """Get all tasks created today"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tasks = self.db.query(Task).filter(
            Task.created_at >= today_start,
            Task.status.in_(["pending", "in_progress"])
        ).all()

        # Enrich with patient data
        result = []
        for task in tasks:
            patient = self.db.query(Patient).filter(Patient.id == task.patient_id).first()
            task_dict = task.to_dict()
            if patient:
                task_dict["patient_name"] = patient.name
                task_dict["patient_blood_group"] = patient.blood_group
                task_dict["patient_phone"] = patient.phone
                task_dict["patient_location"] = patient.location
            result.append(task_dict)

        return result
