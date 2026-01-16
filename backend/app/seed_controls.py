"""
Seed NIST CSF 2.0 controls into the database.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.database import engine
from app.models import Control

CSF_CONTROLS = [
    # Govern Function (NEW in CSF 2.0)
    {
        "csf_id": "GV.OC-1",
        "subcategory": "GV.OC-1",
        "function": "Govern",
        "category": "GV.OC",
        "name": "Organizational Context",
        "text": "The organizational mission, objectives, stakeholders, and activities are understood and inform cybersecurity risk management",
        "keywords": "mission, objectives, stakeholders, organizational context, risk management strategy"
    },
    {
        "csf_id": "GV.RM-1",
        "subcategory": "GV.RM-1",
        "function": "Govern",
        "category": "GV.RM",
        "name": "Risk Management Strategy",
        "text": "Risk management objectives are established and agreed to by organizational stakeholders",
        "keywords": "risk strategy, risk objectives, risk appetite, risk tolerance, stakeholder agreement"
    },
    {
        "csf_id": "GV.RR-1",
        "subcategory": "GV.RR-1",
        "function": "Govern",
        "category": "GV.RR",
        "name": "Roles and Responsibilities",
        "text": "Organizational cybersecurity roles, responsibilities, and authorities are established, communicated, understood, and enforced",
        "keywords": "roles, responsibilities, authority, accountability, RACI, organizational structure"
    },
    {
        "csf_id": "GV.PO-1",
        "subcategory": "GV.PO-1",
        "function": "Govern",
        "category": "GV.PO",
        "name": "Policy",
        "text": "Policy for managing cybersecurity risks is established based on organizational context, cybersecurity strategy, and priorities",
        "keywords": "policy, cybersecurity policy, information security policy, acceptable use policy"
    },
    {
        "csf_id": "GV.OV-1",
        "subcategory": "GV.OV-1",
        "function": "Govern",
        "category": "GV.OV",
        "name": "Oversight",
        "text": "Cybersecurity risk management accountability, authority, and responsibility are established, communicated, and enforced",
        "keywords": "oversight, governance, board oversight, executive oversight, accountability"
    },
    
    # Identify Function
    {
        "csf_id": "ID.AM-1",
        "subcategory": "ID.AM-1",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Asset Management",
        "text": "Physical devices and systems within the organization are inventoried",
        "keywords": "asset inventory, hardware inventory, device inventory, configuration management database"
    },
    {
        "csf_id": "ID.AM-2",
        "subcategory": "ID.AM-2",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Software Inventory",
        "text": "Software platforms and applications within the organization are inventoried",
        "keywords": "software inventory, application inventory, license management"
    },
    {
        "csf_id": "ID.RA-1",
        "subcategory": "ID.RA-1",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Risk Assessment",
        "text": "Vulnerabilities are identified and documented",
        "keywords": "vulnerability assessment, risk assessment, threat identification, vulnerability scanning"
    },
    {
        "csf_id": "ID.RA-2",
        "subcategory": "ID.RA-2",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Threat Intelligence",
        "text": "Cyber threat intelligence is received from information sharing forums and sources",
        "keywords": "threat intelligence, threat feeds, information sharing, ISAC, security advisories"
    },
    
    # Protect Function
    {
        "csf_id": "PR.AC-1",
        "subcategory": "PR.AC-1",
        "function": "Protect",
        "category": "PR.AC",
        "name": "Identity Management",
        "text": "Identities and credentials are issued, managed, verified, revoked, and audited",
        "keywords": "identity management, credential management, user provisioning, IAM"
    },
    {
        "csf_id": "PR.AC-3",
        "subcategory": "PR.AC-3",
        "function": "Protect",
        "category": "PR.AC",
        "name": "Access Control",
        "text": "Remote access is managed",
        "keywords": "remote access, VPN, remote desktop, telecommuting, remote work"
    },
    {
        "csf_id": "PR.AC-4",
        "subcategory": "PR.AC-4",
        "function": "Protect",
        "category": "PR.AC",
        "name": "Access Permissions",
        "text": "Access permissions and authorizations are managed, incorporating principles of least privilege and separation of duties",
        "keywords": "least privilege, separation of duties, access control, authorization, RBAC"
    },
    {
        "csf_id": "PR.AT-1",
        "subcategory": "PR.AT-1",
        "function": "Protect",
        "category": "PR.AT",
        "name": "Security Awareness",
        "text": "All users are informed and trained on their cybersecurity roles and responsibilities",
        "keywords": "security awareness, security training, user education, phishing training"
    },
    {
        "csf_id": "PR.DS-1",
        "subcategory": "PR.DS-1",
        "function": "Protect",
        "category": "PR.DS",
        "name": "Data at Rest",
        "text": "Data-at-rest is protected",
        "keywords": "encryption at rest, data encryption, disk encryption, database encryption"
    },
    {
        "csf_id": "PR.DS-2",
        "subcategory": "PR.DS-2",
        "function": "Protect",
        "category": "PR.DS",
        "name": "Data in Transit",
        "text": "Data-in-transit is protected",
        "keywords": "encryption in transit, TLS, SSL, HTTPS, VPN, secure transmission"
    },
    {
        "csf_id": "PR.IP-1",
        "subcategory": "PR.IP-1",
        "function": "Protect",
        "category": "PR.IP",
        "name": "Configuration Management",
        "text": "A baseline configuration of information technology/industrial control systems is created and maintained",
        "keywords": "configuration management, baseline configuration, configuration hardening, security hardening"
    },
    
    # Detect Function
    {
        "csf_id": "DE.AE-1",
        "subcategory": "DE.AE-1",
        "function": "Detect",
        "category": "DE.AE",
        "name": "Anomaly Detection",
        "text": "A baseline of network operations and expected data flows is established and managed",
        "keywords": "anomaly detection, baseline, network monitoring, behavioral analysis"
    },
    {
        "csf_id": "DE.CM-1",
        "subcategory": "DE.CM-1",
        "function": "Detect",
        "category": "DE.CM",
        "name": "Network Monitoring",
        "text": "The network is monitored to detect potential cybersecurity events",
        "keywords": "network monitoring, IDS, IPS, network security monitoring, packet inspection"
    },
    {
        "csf_id": "DE.CM-3",
        "subcategory": "DE.CM-3",
        "function": "Detect",
        "category": "DE.CM",
        "name": "Personnel Activity Monitoring",
        "text": "Personnel activity is monitored to detect potential cybersecurity events",
        "keywords": "user activity monitoring, insider threat, privileged user monitoring, UBA"
    },
    {
        "csf_id": "DE.CM-7",
        "subcategory": "DE.CM-7",
        "function": "Detect",
        "category": "DE.CM",
        "name": "Unauthorized Activity",
        "text": "Monitoring for unauthorized personnel, connections, devices, and software is performed",
        "keywords": "unauthorized access, rogue devices, shadow IT, unauthorized software"
    },
    {
        "csf_id": "DE.DP-1",
        "subcategory": "DE.DP-1",
        "function": "Detect",
        "category": "DE.DP",
        "name": "Detection Process",
        "text": "Roles and responsibilities for detection are well defined",
        "keywords": "detection roles, SOC, security operations, incident detection, SIEM"
    },
    
    # Respond Function
    {
        "csf_id": "RS.AN-1",
        "subcategory": "RS.AN-1",
        "function": "Respond",
        "category": "RS.AN",
        "name": "Incident Analysis",
        "text": "Notifications from detection systems are investigated",
        "keywords": "incident analysis, alert triage, security investigation, incident response"
    },
    {
        "csf_id": "RS.AN-2",
        "subcategory": "RS.AN-2",
        "function": "Respond",
        "category": "RS.AN",
        "name": "Impact Assessment",
        "text": "The impact of the incident is understood",
        "keywords": "impact analysis, incident severity, business impact, damage assessment"
    },
    {
        "csf_id": "RS.CO-1",
        "subcategory": "RS.CO-1",
        "function": "Respond",
        "category": "RS.CO",
        "name": "Response Communications",
        "text": "Personnel know their roles and order of operations when a response is needed",
        "keywords": "incident response plan, response procedures, escalation, communication plan"
    },
    {
        "csf_id": "RS.MI-1",
        "subcategory": "RS.MI-1",
        "function": "Respond",
        "category": "RS.MI",
        "name": "Incident Mitigation",
        "text": "Incidents are contained and mitigated",
        "keywords": "containment, mitigation, incident remediation, threat neutralization"
    },
    {
        "csf_id": "RS.RP-1",
        "subcategory": "RS.RP-1",
        "function": "Respond",
        "category": "RS.RP",
        "name": "Response Planning",
        "text": "Response plan is executed during or after an incident",
        "keywords": "response execution, incident handling, playbook execution, response coordination"
    },
    
    # Recover Function
    {
        "csf_id": "RC.RP-1",
        "subcategory": "RC.RP-1",
        "function": "Recover",
        "category": "RC.RP",
        "name": "Recovery Planning",
        "text": "Recovery plan is executed during or after a cybersecurity incident",
        "keywords": "recovery plan, business continuity, disaster recovery, restoration"
    },
    {
        "csf_id": "RC.CO-1",
        "subcategory": "RC.CO-1",
        "function": "Recover",
        "category": "RC.CO",
        "name": "Recovery Communications",
        "text": "Public relations are managed and restoration activities are coordinated",
        "keywords": "crisis communication, stakeholder communication, recovery coordination, public relations"
    }
]


def seed_controls():
    """Seed the database with NIST CSF 2.0 controls."""
    print(f"Seeding {len(CSF_CONTROLS)} NIST CSF controls...")

    with Session(engine) as session:
        added = 0
        updated = 0
        
        for control_data in CSF_CONTROLS:
            # Check if control exists
            existing = session.exec(
                select(Control).where(Control.csf_id == control_data["csf_id"])
            ).first()
            
            if existing:
                # Update existing control
                for key, value in control_data.items():
                    setattr(existing, key, value)
                updated += 1
            else:
                # Add new control
                control = Control(**control_data)
                session.add(control)
                added += 1
        
        session.commit()
        print(f"✓ Added {added} new controls, updated {updated} existing controls")

        # Print summary
        print("\nControls by function:")
        function_counts = {}
        for control_data in CSF_CONTROLS:
            func = control_data["function"]
            function_counts[func] = function_counts.get(func, 0) + 1

        for func, count in sorted(function_counts.items()):
            print(f"  {func}: {count}")


if __name__ == "__main__":
    seed_controls()

