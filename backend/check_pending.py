from app.database import engine
from sqlmodel import Session, select
from app.models import Evidence

s = Session(engine)
pending = s.exec(select(Evidence).where(Evidence.status == 'pending')).all()
print(f'Pending evidence items: {len(pending)}')
for e in pending:
    print(f'  ID {e.id}: control_id={e.control_id}, status={e.status}')

all_evidence = s.exec(select(Evidence)).all()
print(f'\nTotal evidence: {len(all_evidence)}')
for e in all_evidence:
    print(f'  ID {e.id}: status={e.status}, type={e.evidence_type}')
