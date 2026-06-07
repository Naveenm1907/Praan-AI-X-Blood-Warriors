"""
Test workflow creation from patient page to coordinator display
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_workflow_creation():
    print("=" * 80)
    print("TESTING WORKFLOW CREATION")
    print("=" * 80)

    # Step 1: Check existing patients
    print("\n1. Checking existing patients...")
    try:
        response = requests.get(f"{BASE_URL}/api/patient/")
        patients = response.json()
        print(f"   ✓ Found {len(patients)} patients")
        if patients:
            patient_id = patients[0]['id']
            patient_name = patients[0]['name']
            print(f"   → Will use patient ID {patient_id}: {patient_name}")
        else:
            print("   ✗ No patients found. Please add a patient first.")
            return
    except Exception as e:
        print(f"   ✗ Failed to fetch patients: {e}")
        return

    # Step 2: Start workflow for the patient
    print(f"\n2. Starting workflow for patient ID {patient_id}...")
    try:
        response = requests.post(f"{BASE_URL}/api/workflow/start-for-patient/{patient_id}")
        if response.status_code == 200:
            result = response.json()
            print(f"   ✓ Workflow created successfully")
            print(f"   → Workflow ID: {result.get('workflow_id', 'N/A')}")
            print(f"   → Message: {result.get('message', 'N/A')}")
        else:
            print(f"   ✗ Failed to create workflow: {response.status_code}")
            print(f"   → Response: {response.text}")
            return
    except Exception as e:
        print(f"   ✗ Error calling workflow endpoint: {e}")
        return

    # Step 3: Check active workflows
    print("\n3. Checking active workflows...")
    try:
        response = requests.get(f"{BASE_URL}/api/workflow/active")
        workflows = response.json()
        print(f"   ✓ Found {len(workflows)} active workflows")

        if workflows:
            workflow = workflows[0]
            print(f"\n   Workflow Details:")
            print(f"   → ID: {workflow.get('workflow_id')}")
            print(f"   → Patient ID: {workflow.get('patient_id')}")
            print(f"   → Current Step: {workflow.get('current_step')}")
            print(f"   → Created At: {workflow.get('created_at')}")

            patient_data = workflow.get('patient_data', {})
            if patient_data:
                print(f"   → Patient Name: {patient_data.get('name')}")
                print(f"   → Blood Group: {patient_data.get('blood_group')}")

            steps = workflow.get('steps', [])
            if steps:
                print(f"   → Total Steps: {len(steps)}")
                completed = sum(1 for s in steps if s.get('status') == 'completed')
                print(f"   → Completed: {completed}/{len(steps)}")
        else:
            print("   ⚠ No active workflows found (workflow may be completed or missing)")
    except Exception as e:
        print(f"   ✗ Failed to fetch active workflows: {e}")

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Open Coordinator page: http://localhost:3000/admin/coordinator")
    print("2. You should see the workflow in the left panel")
    print("3. Click on it to view the timeline and ranked donors")
    print()

if __name__ == "__main__":
    test_workflow_creation()
