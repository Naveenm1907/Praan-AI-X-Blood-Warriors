from sqlalchemy import text
from database import engine

conn = engine.connect()
result = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='patients' AND column_name='id'"))
print(list(result))

result2 = conn.execute(text("SELECT column_name, data_type FROM information_schema.columns WHERE table_name='tasks' AND column_name='patient_id'"))
print(list(result2))
