"""Seed NIST CSF 2.0 controls into the database."""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlmodel import Session, select
from app.database import engine
from app.models import Control


# NIST CSF 2.0 Core Controls (subset for MVP - can be expanded)
CSF_CONTROLS = [
    # IDENTIFY
    {
        "csf_id": "ID.AM-1",
        "function": "Identify",
        "category": "ID.AM",
        "subcategory": "ID.AM-1",
        "name": "Asset Management",
        "text": "Physical devices and systems within the organization are inventoried",
        "keywords": "asset inventory, hardware inventory, device inventory, configuration management database"
    },
    {
        "csf_id": "ID.AM-2",
        "function": "Identify",
        "category": "ID.AM",
        "subcategory": "ID.AM-2",
        "name": "Software Inventory",
        "text": "Software platforms and applications within the organization are inventoried",
        "keywords": "software inventory, application inventory, license management"
    },
    {
        "csf_id": "ID.RA-1",
        "function": "Identify",
        "category": "ID.RA",
        "subcategory": "ID.RA-1",
        "name": "Risk Assessment",
        "text": "Asset vulnerabilities are identified and documented",
        "keywords": "vulnerability assessment, risk assessment, vulnerability scan, penetration test"
    },
    {
        "csf_id": "ID.RA-2",
        "function": "Identify",
        "category": "ID.RA",
        "subcategory": "ID.RA-2",
        "name": "Threat Intelligence",
        "text": "Cyber threat intelligence is received from information sharing forums and sources",
        "keywords": "threat intelligence, threat feeds, information sharing, ISAC"
    },
    
    # PROTECT
    {
        "csf_id": "PR.AC-1",
        "function": "Protect",
        "category": "PR.AC",
        "subcategory": "PR.AC-1",
        "name": "Access Control",
        "text": "Identities and credentials are issued, managed, verified, revoked, and audited for authorized devices, users and processes",
        "keywords": "access control, identity management, authentication, authorization, IAM"
    },
    {
        "csf_id": "PR.AC-3",
        "function": "Protect",
        "category": "PR.AC",
        "subcategory": "PR.AC-3",
        "name": "Remote Access",
        "text": "Remote access is managed",
        "keywords": "remote access, VPN, remote desktop, bastion host, jump server"
    },
    {
        "csf_id": "PR.AC-4",
        "function": "Protect",
        "category": "PR.AC",
        "subcategory": "PR.AC-4",
        "name": "Least Privilege",
        "text": "Access permissions and authorizations are managed, incorporating the principles of least privilege and separation of duties",
        "keywords": "least privilege, separation of duties, role-based access control, RBAC, need to know"
    },
    {
        "csf_id": "PR.AC-7",
        "function": "Protect",
        "category": "PR.AC",
        "subcategory": "PR.AC-7",
        "name": "Multi-Factor Authentication",
        "text": "Users, devices, and other assets are authenticated commensurate with the risk of the transaction",
        "keywords": "multi-factor authentication, MFA, two-factor, 2FA, strong authentication"
    },
    {
        "csf_id": "PR.DS-1",
        "function": "Protect",
        "category": "PR.DS",
        "subcategory": "PR.DS-1",
        "name": "Data at Rest Protection",
        "text": "Data-at-rest is protected",
        "keywords": "encryption at rest, data protection, disk encryption, database encryption"
    },
    {
        "csf_id": "PR.DS-2",
        "function": "Protect",
        "category": "PR.DS",
        "subcategory": "PR.DS-2",
        "name": "Data in Transit Protection",
        "text": "Data-in-transit is protected",
        "keywords": "encryption in transit, TLS, SSL, HTTPS, VPN, data transmission"
    },
    {
        "csf_id": "PR.PT-1",
        "function": "Protect",
        "category": "PR.PT",
        "subcategory": "PR.PT-1",
        "name": "Audit Logging",
        "text": "Audit/log records are determined, documented, implemented, and reviewed",
        "keywords": "audit logs, logging, log management, security logs, audit trail"
    },
    
    # DETECT
    {
        "csf_id": "DE.CM-1",
        "function": "Detect",
        "category": "DE.CM",
        "subcategory": "DE.CM-1",
        "name": "Network Monitoring",
        "text": "The network is monitored to detect potential cybersecurity events",
        "keywords": "network monitoring, IDS, IPS, network security monitoring, traffic analysis"
    },
    {
        "csf_id": "DE.CM-3",
        "function": "Detect",
        "category": "DE.CM",
        "subcategory": "DE.CM-3",
        "name": "Personnel Activity Monitoring",
        "text": "Personnel activity is monitored to detect potential cybersecurity events",
        "keywords": "user activity monitoring, privileged user monitoring, insider threat, behavior analytics"
    },
    {
        "csf_id": "DE.CM-6",
        "function": "Detect",
        "category": "DE.CM",
        "subcategory": "DE.CM-6",
        "name": "External Service Provider Monitoring",
        "text": "External service provider activity is monitored to detect potential cybersecurity events",
        "keywords": "third party monitoring, vendor monitoring, supplier monitoring, external access"
    },
    {
        "csf_id": "DE.CM-7",
        "function": "Detect",
        "category": "DE.CM",
        "subcategory": "DE.CM-7",
        "name": "Continuous Monitoring",
        "text": "Monitoring for unauthorized personnel, connections, devices, and software is performed",
        "keywords": "continuous monitoring, security monitoring, SIEM, security operations center, SOC"
    },
    {
        "csf_id": "DE.AE-1",
        "function": "Detect",
        "category": "DE.AE",
        "subcategory": "DE.AE-1",
        "name": "Anomaly Detection",
        "text": "A baseline of network operations and expected data flows is established and managed",
        "keywords": "anomaly detection, baseline, normal behavior, deviation, outlier"
    },
    
    # RESPOND
    {
        "csf_id": "RS.RP-1",
        "function": "Respond",
        "category": "RS.RP",
        "subcategory": "RS.RP-1",
        "name": "Response Plan",
        "text": "Response plan is executed during or after an incident",
        "keywords": "incident response plan, response procedures, incident handling, response execution"
    },
    {
        "csf_id": "RS.CO-2",
        "function": "Respond",
        "category": "RS.CO",
        "subcategory": "RS.CO-2",
        "name": "Incident Reporting",
        "text": "Incidents are reported consistent with established criteria",
        "keywords": "incident reporting, security incident, breach notification, incident escalation"
    },
    {
        "csf_id": "RS.AN-1",
        "function": "Respond",
        "category": "RS.AN",
        "subcategory": "RS.AN-1",
        "name": "Incident Investigation",
        "text": "Notifications from detection systems are investigated",
        "keywords": "incident investigation, forensics, root cause analysis, incident analysis"
    },
    {
        "csf_id": "RS.MI-1",
        "function": "Respond",
        "category": "RS.MI",
        "subcategory": "RS.MI-1",
        "name": "Incident Containment",
        "text": "Incidents are contained",
        "keywords": "containment, isolation, quarantine, incident mitigation"
    },
    {
        "csf_id": "RS.MI-2",
        "function": "Respond",
        "category": "RS.MI",
        "subcategory": "RS.MI-2",
        "name": "Incident Mitigation",
        "text": "Incidents are mitigated",
        "keywords": "mitigation, remediation, incident response, recovery actions"
    },
    
    # RECOVER
    {
        "csf_id": "RC.RP-1",
        "function": "Recover",
        "category": "RC.RP",
        "subcategory": "RC.RP-1",
        "name": "Recovery Plan",
        "text": "Recovery plan is executed during or after a cybersecurity incident",
        "keywords": "recovery plan, disaster recovery, business continuity, recovery procedures"
    },
    {
        "csf_id": "RC.CO-3",
        "function": "Recover",
        "category": "RC.CO",
        "subcategory": "RC.CO-3",
        "name": "Recovery Communications",
        "text": "Public relations are managed",
        "keywords": "communications, public relations, stakeholder notification, recovery communications"
    },
]


def seed_controls():
    """Seed CSF controls into the database."""
    with Session(engine) as session:
        # Check if controls already exist
        statement = select(Control)
        existing = session.exec(statement).first()
        
        if existing:
            print("⚠ Controls already exist in database. Skipping seed.")
            print("  To reseed, delete the database and run init_db.py first.")
            return
        
        print(f"Seeding {len(CSF_CONTROLS)} NIST CSF controls...")
        
        for control_data in CSF_CONTROLS:
            control = Control(**control_data)
            session.add(control)
        
        session.commit()
        print(f"✓ Successfully seeded {len(CSF_CONTROLS)} controls!")
        
        # Print summary by function
        functions = {}
        for control in CSF_CONTROLS:
            func = control["function"]
            functions[func] = functions.get(func, 0) + 1
        
        print("\nControls by function:")
        for func, count in sorted(functions.items()):
            print(f"  {func}: {count}")


if __name__ == "__main__":
    seed_controls()
