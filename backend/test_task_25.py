"""Test script to reproduce task 25 error with full traceback"""
import sys
sys.path.insert(0, 'E:\\dev\\blendai\\Ai for good 2.0\\backend')

from database import get_db
from database.models import Donor as DonorDB
from models.task import Task

db = next(get_db())

# Get task 25
task = db.query(Task).filter(Task.id == 25).first()
if not task:
    print("Task 25 not found")
    sys.exit(1)

print(f"Task 25 found: patient_id={task.patient_id}")

task_dict = task.to_dict()
assigned_donors = task_dict.get("assigned_donors") or []
print(f"Assigned donors: {len(assigned_donors)}")

if assigned_donors:
    # NEW LOGIC: Convert 'd01' -> 'D001'
    user_ids = []
    for d in assigned_donors:
        donor_id_str = d["donor_id"]
        if isinstance(donor_id_str, str) and donor_id_str.startswith('d'):
            user_id = 'D' + donor_id_str[1:].zfill(3)
            user_ids.append(user_id)
            print(f"  {donor_id_str} -> {user_id}")
        else:
            user_ids.append(str(donor_id_str))

    print(f"\nQuerying donors with user_ids: {user_ids}")
    donors = db.query(DonorDB).filter(DonorDB.user_id.in_(user_ids)).all()
    print(f"Found {len(donors)} donors")

    for donor in donors:
        print(f"  user_id={donor.user_id}, id={donor.id}, phone={donor.phone}")

print("\nSUCCESS!")
