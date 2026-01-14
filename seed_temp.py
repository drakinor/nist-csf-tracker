import sqlite3
conn = sqlite3.connect(r'C:\nist-csf-tracker\data\nist_csf_tracker.db')
c = conn.cursor()
c.execute('DELETE FROM controls')
controls = [
    ('GV.OC-1', 'Govern', 'GV.OC', 'GV.OC-1', 'Organizational Context', 'The organizational mission, objectives, stakeholders, and activities are understood and inform cybersecurity risk management', 'mission, objectives, stakeholders, organizational context, risk management strategy'),
    ('GV.RM-1', 'Govern', 'GV.RM', 'GV.RM-1', 'Risk Management Strategy', 'Risk management objectives are established and agreed to by organizational stakeholders', 'risk strategy, risk objectives, risk appetite, risk tolerance, stakeholder agreement'),
    ('GV.RR-1', 'Govern', 'GV.RR', 'GV.RR-1', 'Roles and Responsibilities', 'Organizational cybersecurity roles, responsibilities, and authorities are established, communicated, understood, and enforced', 'roles, responsibilities, authority, accountability, RACI, organizational structure'),
    ('GV.PO-1', 'Govern', 'GV.PO', 'GV.PO-1', 'Policy', 'Policy for managing cybersecurity risks is established based on organizational context, cybersecurity strategy, and priorities', 'policy, cybersecurity policy, information security policy, acceptable use policy'),
    ('GV.OV-1', 'Govern', 'GV.OV', 'GV.OV-1', 'Oversight', 'Cybersecurity risk management accountability, authority, and responsibility are established, communicated, and enforced', 'oversight, governance, board oversight, executive oversight, accountability'),
    ('ID.AM-1', 'Identify', 'ID.AM', 'ID.AM-1', 'Asset Management', 'Physical devices and systems within the organization are inventoried', 'asset inventory, hardware inventory, device inventory, configuration management database'),
    ('ID.AM-2', 'Identify', 'ID.AM', 'ID.AM-2', 'Software Inventory', 'Software platforms and applications within the organization are inventoried', 'software inventory, application inventory, license management'),
    ('ID.RA-1', 'Identify', 'ID.RA', 'ID.RA-1', 'Risk Assessment', 'Vulnerabilities are identified and documented', 'vulnerability assessment, risk assessment, threat identification, vulnerability scanning'),
    ('ID.RA-2', 'Identify', 'ID.RA', 'ID.RA-2', 'Threat Intelligence', 'Cyber threat intelligence is received from information sharing forums and sources', 'threat intelligence, threat feeds, information sharing, ISAC, security advisories'),
    ('PR.AC-1', 'Protect', 'PR.AC', 'PR.AC-1', 'Identity Management', 'Identities and credentials are issued, managed, verified, revoked, and audited', 'identity management, credential management, user provisioning, IAM'),
    ('PR.AC-3', 'Protect', 'PR.AC', 'PR.AC-3', 'Access Control', 'Remote access is managed', 'remote access, VPN, remote desktop, telecommuting, remote work'),
    ('PR.AC-4', 'Protect', 'PR.AC', 'PR.AC-4', 'Access Permissions', 'Access permissions and authorizations are managed, incorporating principles of least privilege and separation of duties', 'least privilege, separation of duties, access control, authorization, RBAC'),
    ('PR.AT-1', 'Protect', 'PR.AT', 'PR.AT-1', 'Security Awareness', 'All users are informed and trained on their cybersecurity roles and responsibilities', 'security awareness, security training, user education, phishing training'),
    ('PR.DS-1', 'Protect', 'PR.DS', 'PR.DS-1', 'Data at Rest', 'Data-at-rest is protected', 'encryption at rest, data encryption, disk encryption, database encryption'),
    ('PR.DS-2', 'Protect', 'PR.DS', 'PR.DS-2', 'Data in Transit', 'Data-in-transit is protected', 'encryption in transit, TLS, SSL, HTTPS, VPN, secure transmission'),
    ('PR.IP-1', 'Protect', 'PR.IP', 'PR.IP-1', 'Configuration Management', 'A baseline configuration of information technology/industrial control systems is created and maintained', 'configuration management, baseline configuration, configuration hardening, security hardening'),
    ('DE.AE-1', 'Detect', 'DE.AE', 'DE.AE-1', 'Anomaly Detection', 'A baseline of network operations and expected data flows is established and managed', 'anomaly detection, baseline, network monitoring, behavioral analysis'),
    ('DE.CM-1', 'Detect', 'DE.CM', 'DE.CM-1', 'Network Monitoring', 'The network is monitored to detect potential cybersecurity events', 'network monitoring, IDS, IPS, network security monitoring, packet inspection'),
    ('DE.CM-3', 'Detect', 'DE.CM', 'DE.CM-3', 'Personnel Activity Monitoring', 'Personnel activity is monitored to detect potential cybersecurity events', 'user activity monitoring, insider threat, privileged user monitoring, UBA'),
    ('DE.CM-7', 'Detect', 'DE.CM', 'DE.CM-7', 'Unauthorized Activity', 'Monitoring for unauthorized personnel, connections, devices, and software is performed', 'unauthorized access, rogue devices, shadow IT, unauthorized software'),
    ('DE.DP-1', 'Detect', 'DE.DP', 'DE.DP-1', 'Detection Process', 'Roles and responsibilities for detection are well defined', 'detection roles, SOC, security operations, incident detection, SIEM'),
    ('RS.AN-1', 'Respond', 'RS.AN', 'RS.AN-1', 'Incident Analysis', 'Notifications from detection systems are investigated', 'incident analysis, alert triage, security investigation, incident response'),
    ('RS.AN-2', 'Respond', 'RS.AN', 'RS.AN-2', 'Impact Assessment', 'The impact of the incident is understood', 'impact analysis, incident severity, business impact, damage assessment'),
    ('RS.CO-1', 'Respond', 'RS.CO', 'RS.CO-1', 'Response Communications', 'Personnel know their roles and order of operations when a response is needed', 'incident response plan, response procedures, escalation, communication plan'),
    ('RS.MI-1', 'Respond', 'RS.MI', 'RS.MI-1', 'Incident Mitigation', 'Incidents are contained and mitigated', 'containment, mitigation, incident remediation, threat neutralization'),
    ('RS.RP-1', 'Respond', 'RS.RP', 'RS.RP-1', 'Response Planning', 'Response plan is executed during or after an incident', 'response execution, incident handling, playbook execution, response coordination'),
    ('RC.RP-1', 'Recover', 'RC.RP', 'RC.RP-1', 'Recovery Planning', 'Recovery plan is executed during or after a cybersecurity incident', 'recovery plan, business continuity, disaster recovery, restoration'),
    ('RC.CO-1', 'Recover', 'RC.CO', 'RC.CO-1', 'Recovery Communications', 'Public relations are managed and restoration activities are coordinated', 'crisis communication, stakeholder communication, recovery coordination, public relations')
]
c.executemany('INSERT INTO controls (csf_id, function, category, subcategory, name, text, keywords) VALUES (?, ?, ?, ?, ?, ?, ?)', controls)
conn.commit()
print(f'Seeded {len(controls)} controls')
print(f'Govern: {sum(1 for x in controls if x[1]=="Govern")}')
print(f'Identify: {sum(1 for x in controls if x[1]=="Identify")}')
print(f'Protect: {sum(1 for x in controls if x[1]=="Protect")}')
print(f'Detect: {sum(1 for x in controls if x[1]=="Detect")}')
print(f'Respond: {sum(1 for x in controls if x[1]=="Respond")}')
print(f'Recover: {sum(1 for x in controls if x[1]=="Recover")}')
conn.close()
