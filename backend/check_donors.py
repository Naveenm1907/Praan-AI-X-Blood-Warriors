from database import get_db
from database.models import Donor

db = next(get_db())
donors = db.query(Donor).limit(20).all()

for d in donors:
    print(f"ID={d.id}, user_id={d.user_id}, phone={d.phone}")
