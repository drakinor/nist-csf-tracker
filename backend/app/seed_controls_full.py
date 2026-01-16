"""
Seed NIST CSF 2.0 controls into the database - COMPLETE LIST (106 Subcategories).
Based on NIST CSWP 29, February 26, 2024
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlmodel import Session, select
from app.database import engine
from app.models import Control

CSF_CONTROLS = [
    # GOVERN (GV) - 31 Subcategories
    # Organizational Context (GV.OC)
    {
        "csf_id": "GV.OC-01",
        "subcategory": "GV.OC-01",
        "function": "Govern",
        "category": "GV.OC",
        "name": "Organizational Context",
        "text": "The organizational mission is understood and informs cybersecurity risk management",
        "keywords": "mission, objectives, organizational context"
    },
    {
        "csf_id": "GV.OC-02",
        "subcategory": "GV.OC-02",
        "function": "Govern",
        "category": "GV.OC",
        "name": "Stakeholder Understanding",
        "text": "Internal and external stakeholders are understood, and their needs and expectations regarding cybersecurity risk management are understood and considered",
        "keywords": "stakeholders, expectations, needs"
    },
    {
        "csf_id": "GV.OC-03",
        "subcategory": "GV.OC-03",
        "function": "Govern",
        "category": "GV.OC",
        "name": "Legal and Regulatory Requirements",
        "text": "Legal, regulatory, and contractual requirements regarding cybersecurity — including privacy and civil liberties obligations — are understood and managed",
        "keywords": "legal, regulatory, compliance, contractual, privacy"
    },
    {
        "csf_id": "GV.OC-04",
        "subcategory": "GV.OC-04",
        "function": "Govern",
        "category": "GV.OC",
        "name": "Critical Objectives and Services",
        "text": "Critical objectives, capabilities, and services that external stakeholders depend on or expect from the organization are understood and communicated",
        "keywords": "critical services, dependencies, external stakeholders"
    },
    {
        "csf_id": "GV.OC-05",
        "subcategory": "GV.OC-05",
        "function": "Govern",
        "category": "GV.OC",
        "name": "Dependencies",
        "text": "Outcomes, capabilities, and services that the organization depends on are understood and communicated",
        "keywords": "dependencies, services, capabilities"
    },
    # Risk Management Strategy (GV.RM)
    {
        "csf_id": "GV.RM-01",
        "subcategory": "GV.RM-01",
        "function": "Govern",
        "category": "GV.RM",
        "name": "Risk Management Objectives",
        "text": "Risk management objectives are established and agreed to by organizational stakeholders",
        "keywords": "risk objectives, risk strategy"
    },
    {
        "csf_id": "GV.RM-02",
        "subcategory": "GV.RM-02",
        "function": "Govern",
        "category": "GV.RM",
        "name": "Risk Appetite and Tolerance",
        "text": "Risk appetite and risk tolerance statements are established, communicated, and maintained",
        "keywords": "risk appetite, risk tolerance"
    },
    {
        "csf_id": "GV.RM-03",
        "subcategory": "GV.RM-03",
        "function": "Govern",
        "category": "GV.RM",
        "name": "Enterprise Risk Integration",
        "text": "Cybersecurity risk management activities and outcomes are included in enterprise risk management processes",
        "keywords": "enterprise risk management, ERM, integration"
    },
    {
        "csf_id": "GV.RM-04",
        "subcategory": "GV.RM-04",
        "function": "Govern",
        "category": "GV.RM",
        "name": "Risk Response Strategy",
        "text": "Strategic direction that describes appropriate risk response options is established and communicated",
        "keywords": "risk response, mitigation strategy"
    },
    {
        "csf_id": "GV.RM-05",
        "subcategory": "GV.RM-05",
        "function": "Govern",
        "category": "GV.RM",
        "name": "Risk Communication",
        "text": "Lines of communication across the organization are established for cybersecurity risks, including risks from suppliers and other third parties",
        "keywords": "communication, risk reporting, escalation"
    },
    {
        "csf_id": "GV.RM-06",
        "subcategory": "GV.RM-06",
        "function": "Govern",
        "category": "GV.RM",
        "name": "Risk Calculation Method",
        "text": "A standardized method for calculating, documenting, categorizing, and prioritizing cybersecurity risks is established and communicated",
        "keywords": "risk calculation, risk scoring, methodology"
    },
    {
        "csf_id": "GV.RM-07",
        "subcategory": "GV.RM-07",
        "function": "Govern",
        "category": "GV.RM",
        "name": "Strategic Opportunities",
        "text": "Strategic opportunities (i.e., positive risks) are characterized and are included in organizational cybersecurity risk discussions",
        "keywords": "opportunities, positive risks, strategic advantage"
    },
    # Roles, Responsibilities, and Authorities (GV.RR)
    {
        "csf_id": "GV.RR-01",
        "subcategory": "GV.RR-01",
        "function": "Govern",
        "category": "GV.RR",
        "name": "Leadership Accountability",
        "text": "Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, ethical, and continually improving",
        "keywords": "leadership, accountability, culture"
    },
    {
        "csf_id": "GV.RR-02",
        "subcategory": "GV.RR-02",
        "function": "Govern",
        "category": "GV.RR",
        "name": "Roles and Responsibilities",
        "text": "Roles, responsibilities, and authorities related to cybersecurity risk management are established, communicated, understood, and enforced",
        "keywords": "roles, responsibilities, RACI"
    },
    {
        "csf_id": "GV.RR-03",
        "subcategory": "GV.RR-03",
        "function": "Govern",
        "category": "GV.RR",
        "name": "Resource Allocation",
        "text": "Adequate resources are allocated commensurate with the cybersecurity risk strategy, roles, responsibilities, and policies",
        "keywords": "resources, budget, funding"
    },
    {
        "csf_id": "GV.RR-04",
        "subcategory": "GV.RR-04",
        "function": "Govern",
        "category": "GV.RR",
        "name": "Cybersecurity in HR Practices",
        "text": "Cybersecurity is included in human resources practices",
        "keywords": "human resources, personnel, hiring, training"
    },
    # Policy (GV.PO)
    {
        "csf_id": "GV.PO-01",
        "subcategory": "GV.PO-01",
        "function": "Govern",
        "category": "GV.PO",
        "name": "Policy Establishment",
        "text": "Policy for managing cybersecurity risks is established based on organizational context, cybersecurity strategy, and priorities and is communicated and enforced",
        "keywords": "policy, cybersecurity policy"
    },
    {
        "csf_id": "GV.PO-02",
        "subcategory": "GV.PO-02",
        "function": "Govern",
        "category": "GV.PO",
        "name": "Policy Review and Update",
        "text": "Policy for managing cybersecurity risks is reviewed, updated, communicated, and enforced to reflect changes in requirements, threats, technology, and organizational mission",
        "keywords": "policy review, policy update"
    },
    # Oversight (GV.OV)
    {
        "csf_id": "GV.OV-01",
        "subcategory": "GV.OV-01",
        "function": "Govern",
        "category": "GV.OV",
        "name": "Strategy Outcome Review",
        "text": "Cybersecurity risk management strategy outcomes are reviewed to inform and adjust strategy and direction",
        "keywords": "strategy review, oversight"
    },
    {
        "csf_id": "GV.OV-02",
        "subcategory": "GV.OV-02",
        "function": "Govern",
        "category": "GV.OV",
        "name": "Strategy Coverage Review",
        "text": "The cybersecurity risk management strategy is reviewed and adjusted to ensure coverage of organizational requirements and risks",
        "keywords": "strategy coverage, gap analysis"
    },
    {
        "csf_id": "GV.OV-03",
        "subcategory": "GV.OV-03",
        "function": "Govern",
        "category": "GV.OV",
        "name": "Performance Evaluation",
        "text": "Organizational cybersecurity risk management performance is evaluated and reviewed for adjustments needed",
        "keywords": "performance evaluation, metrics, KPIs"
    },
    # Cybersecurity Supply Chain Risk Management (GV.SC)
    {
        "csf_id": "GV.SC-01",
        "subcategory": "GV.SC-01",
        "function": "Govern",
        "category": "GV.SC",
        "name": "C-SCRM Program",
        "text": "A cybersecurity supply chain risk management program, strategy, objectives, policies, and processes are established and agreed to by organizational stakeholders",
        "keywords": "supply chain, C-SCRM, supply chain risk"
    },
    {
        "csf_id": "GV.SC-02",
        "subcategory": "GV.SC-02",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Supplier Roles and Responsibilities",
        "text": "Cybersecurity roles and responsibilities for suppliers, customers, and partners are established, communicated, and coordinated internally and externally",
        "keywords": "supplier responsibilities, third party roles"
    },
    {
        "csf_id": "GV.SC-03",
        "subcategory": "GV.SC-03",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Supply Chain Integration",
        "text": "Cybersecurity supply chain risk management is integrated into cybersecurity and enterprise risk management, risk assessment, and improvement processes",
        "keywords": "supply chain integration, risk management integration"
    },
    {
        "csf_id": "GV.SC-04",
        "subcategory": "GV.SC-04",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Supplier Prioritization",
        "text": "Suppliers are known and prioritized by criticality",
        "keywords": "supplier inventory, critical suppliers"
    },
    {
        "csf_id": "GV.SC-05",
        "subcategory": "GV.SC-05",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Contractual Requirements",
        "text": "Requirements to address cybersecurity risks in supply chains are established, prioritized, and integrated into contracts and other types of agreements with suppliers and other relevant third parties",
        "keywords": "contracts, agreements, requirements"
    },
    {
        "csf_id": "GV.SC-06",
        "subcategory": "GV.SC-06",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Due Diligence",
        "text": "Planning and due diligence are performed to reduce risks before entering into formal supplier or other third-party relationships",
        "keywords": "due diligence, vendor assessment"
    },
    {
        "csf_id": "GV.SC-07",
        "subcategory": "GV.SC-07",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Supplier Risk Management",
        "text": "The risks posed by a supplier, their products and services, and other third parties are understood, recorded, prioritized, assessed, responded to, and monitored over the course of the relationship",
        "keywords": "supplier risk, third party risk, vendor risk management"
    },
    {
        "csf_id": "GV.SC-08",
        "subcategory": "GV.SC-08",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Supplier Incident Planning",
        "text": "Relevant suppliers and other third parties are included in incident planning, response, and recovery activities",
        "keywords": "supplier incident response, third party incidents"
    },
    {
        "csf_id": "GV.SC-09",
        "subcategory": "GV.SC-09",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Supply Chain Security Practices",
        "text": "Supply chain security practices are integrated into cybersecurity and enterprise risk management programs, and their performance is monitored throughout the technology product and service life cycle",
        "keywords": "supply chain security, lifecycle management"
    },
    {
        "csf_id": "GV.SC-10",
        "subcategory": "GV.SC-10",
        "function": "Govern",
        "category": "GV.SC",
        "name": "Post-Relationship Planning",
        "text": "Cybersecurity supply chain risk management plans include provisions for activities that occur after the conclusion of a partnership or service agreement",
        "keywords": "offboarding, contract termination, data return"
    },
    
    # IDENTIFY (ID) - 22 Subcategories
    # Asset Management (ID.AM)
    {
        "csf_id": "ID.AM-01",
        "subcategory": "ID.AM-01",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Hardware Inventory",
        "text": "Inventories of hardware managed by the organization are maintained",
        "keywords": "hardware inventory, asset inventory, devices"
    },
    {
        "csf_id": "ID.AM-02",
        "subcategory": "ID.AM-02",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Software and Services Inventory",
        "text": "Inventories of software, services, and systems managed by the organization are maintained",
        "keywords": "software inventory, application inventory, services"
    },
    {
        "csf_id": "ID.AM-03",
        "subcategory": "ID.AM-03",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Network Communications",
        "text": "Representations of the organization's authorized network communication and internal and external network data flows are maintained",
        "keywords": "network diagram, data flows, network topology"
    },
    {
        "csf_id": "ID.AM-04",
        "subcategory": "ID.AM-04",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Supplier Services Inventory",
        "text": "Inventories of services provided by suppliers are maintained",
        "keywords": "supplier services, third party services"
    },
    {
        "csf_id": "ID.AM-05",
        "subcategory": "ID.AM-05",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Asset Prioritization",
        "text": "Assets are prioritized based on classification, criticality, resources, and impact on the mission",
        "keywords": "asset classification, criticality, prioritization"
    },
    {
        "csf_id": "ID.AM-07",
        "subcategory": "ID.AM-07",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Data Inventory",
        "text": "Inventories of data and corresponding metadata for designated data types are maintained",
        "keywords": "data inventory, data classification, metadata"
    },
    {
        "csf_id": "ID.AM-08",
        "subcategory": "ID.AM-08",
        "function": "Identify",
        "category": "ID.AM",
        "name": "Lifecycle Management",
        "text": "Systems, hardware, software, services, and data are managed throughout their life cycles",
        "keywords": "lifecycle, asset management, decommissioning"
    },
    # Risk Assessment (ID.RA)
    {
        "csf_id": "ID.RA-01",
        "subcategory": "ID.RA-01",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Vulnerability Identification",
        "text": "Vulnerabilities in assets are identified, validated, and recorded",
        "keywords": "vulnerability management, vulnerability scanning"
    },
    {
        "csf_id": "ID.RA-02",
        "subcategory": "ID.RA-02",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Threat Intelligence",
        "text": "Cyber threat intelligence is received from information sharing forums and sources",
        "keywords": "threat intelligence, threat feeds, ISAC"
    },
    {
        "csf_id": "ID.RA-03",
        "subcategory": "ID.RA-03",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Threat Identification",
        "text": "Internal and external threats to the organization are identified and recorded",
        "keywords": "threat identification, threat modeling"
    },
    {
        "csf_id": "ID.RA-04",
        "subcategory": "ID.RA-04",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Impact Assessment",
        "text": "Potential impacts and likelihoods of threats exploiting vulnerabilities are identified and recorded",
        "keywords": "impact analysis, likelihood, risk assessment"
    },
    {
        "csf_id": "ID.RA-05",
        "subcategory": "ID.RA-05",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Risk Prioritization",
        "text": "Threats, vulnerabilities, likelihoods, and impacts are used to understand inherent risk and inform risk response prioritization",
        "keywords": "inherent risk, risk prioritization"
    },
    {
        "csf_id": "ID.RA-06",
        "subcategory": "ID.RA-06",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Risk Response Selection",
        "text": "Risk responses are chosen, prioritized, planned, tracked, and communicated",
        "keywords": "risk response, risk treatment, mitigation"
    },
    {
        "csf_id": "ID.RA-07",
        "subcategory": "ID.RA-07",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Change Management",
        "text": "Changes and exceptions are managed, assessed for risk impact, recorded, and tracked",
        "keywords": "change management, exception management"
    },
    {
        "csf_id": "ID.RA-08",
        "subcategory": "ID.RA-08",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Vulnerability Disclosure",
        "text": "Processes for receiving, analyzing, and responding to vulnerability disclosures are established",
        "keywords": "vulnerability disclosure, responsible disclosure"
    },
    {
        "csf_id": "ID.RA-09",
        "subcategory": "ID.RA-09",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Hardware and Software Authenticity",
        "text": "The authenticity and integrity of hardware and software are assessed prior to acquisition and use",
        "keywords": "authenticity, integrity, supply chain validation"
    },
    {
        "csf_id": "ID.RA-10",
        "subcategory": "ID.RA-10",
        "function": "Identify",
        "category": "ID.RA",
        "name": "Critical Supplier Assessment",
        "text": "Critical suppliers are assessed prior to acquisition",
        "keywords": "supplier assessment, vendor evaluation"
    },
    # Improvement (ID.IM)
    {
        "csf_id": "ID.IM-01",
        "subcategory": "ID.IM-01",
        "function": "Identify",
        "category": "ID.IM",
        "name": "Improvement from Evaluations",
        "text": "Improvements are identified from evaluations",
        "keywords": "continuous improvement, lessons learned"
    },
    {
        "csf_id": "ID.IM-02",
        "subcategory": "ID.IM-02",
        "function": "Identify",
        "category": "ID.IM",
        "name": "Improvement from Testing",
        "text": "Improvements are identified from security tests and exercises, including those done in coordination with suppliers and relevant third parties",
        "keywords": "security testing, exercises, tabletop"
    },
    {
        "csf_id": "ID.IM-03",
        "subcategory": "ID.IM-03",
        "function": "Identify",
        "category": "ID.IM",
        "name": "Improvement from Operations",
        "text": "Improvements are identified from execution of operational processes, procedures, and activities",
        "keywords": "operational improvements, process optimization"
    },
    {
        "csf_id": "ID.IM-04",
        "subcategory": "ID.IM-04",
        "function": "Identify",
        "category": "ID.IM",
        "name": "Plan Maintenance",
        "text": "Incident response plans and other cybersecurity plans that affect operations are established, communicated, maintained, and improved",
        "keywords": "plan maintenance, incident response plan"
    },
    
    # PROTECT (PR) - 22 Subcategories
    # Identity Management, Authentication, and Access Control (PR.AA)
    {
        "csf_id": "PR.AA-01",
        "subcategory": "PR.AA-01",
        "function": "Protect",
        "category": "PR.AA",
        "name": "Identity and Credential Management",
        "text": "Identities and credentials for authorized users, services, and hardware are managed by the organization",
        "keywords": "identity management, credentials, IAM"
    },
    {
        "csf_id": "PR.AA-02",
        "subcategory": "PR.AA-02",
        "function": "Protect",
        "category": "PR.AA",
        "name": "Identity Proofing",
        "text": "Identities are proofed and bound to credentials based on the context of interactions",
        "keywords": "identity proofing, verification"
    },
    {
        "csf_id": "PR.AA-03",
        "subcategory": "PR.AA-03",
        "function": "Protect",
        "category": "PR.AA",
        "name": "Authentication",
        "text": "Users, services, and hardware are authenticated",
        "keywords": "authentication, MFA, multi-factor"
    },
    {
        "csf_id": "PR.AA-04",
        "subcategory": "PR.AA-04",
        "function": "Protect",
        "category": "PR.AA",
        "name": "Identity Assertions",
        "text": "Identity assertions are protected, conveyed, and verified",
        "keywords": "identity assertions, SSO, federation"
    },
    {
        "csf_id": "PR.AA-05",
        "subcategory": "PR.AA-05",
        "function": "Protect",
        "category": "PR.AA",
        "name": "Access Control",
        "text": "Access permissions, entitlements, and authorizations are defined in a policy, managed, enforced, and reviewed, and incorporate the principles of least privilege and separation of duties",
        "keywords": "access control, least privilege, separation of duties, authorization"
    },
    {
        "csf_id": "PR.AA-06",
        "subcategory": "PR.AA-06",
        "function": "Protect",
        "category": "PR.AA",
        "name": "Physical Access Control",
        "text": "Physical access to assets is managed, monitored, and enforced commensurate with risk",
        "keywords": "physical access, physical security"
    },
    # Awareness and Training (PR.AT)
    {
        "csf_id": "PR.AT-01",
        "subcategory": "PR.AT-01",
        "function": "Protect",
        "category": "PR.AT",
        "name": "General Cybersecurity Awareness",
        "text": "Personnel are provided with awareness and training so that they possess the knowledge and skills to perform general tasks with cybersecurity risks in mind",
        "keywords": "awareness training, security awareness"
    },
    {
        "csf_id": "PR.AT-02",
        "subcategory": "PR.AT-02",
        "function": "Protect",
        "category": "PR.AT",
        "name": "Specialized Training",
        "text": "Individuals in specialized roles are provided with awareness and training so that they possess the knowledge and skills to perform relevant tasks with cybersecurity risks in mind",
        "keywords": "specialized training, role-based training"
    },
    # Data Security (PR.DS)
    {
        "csf_id": "PR.DS-01",
        "subcategory": "PR.DS-01",
        "function": "Protect",
        "category": "PR.DS",
        "name": "Data-at-Rest Protection",
        "text": "The confidentiality, integrity, and availability of data-at-rest are protected",
        "keywords": "data at rest, encryption, storage security"
    },
    {
        "csf_id": "PR.DS-02",
        "subcategory": "PR.DS-02",
        "function": "Protect",
        "category": "PR.DS",
        "name": "Data-in-Transit Protection",
        "text": "The confidentiality, integrity, and availability of data-in-transit are protected",
        "keywords": "data in transit, TLS, encryption, network security"
    },
    {
        "csf_id": "PR.DS-10",
        "subcategory": "PR.DS-10",
        "function": "Protect",
        "category": "PR.DS",
        "name": "Data-in-Use Protection",
        "text": "The confidentiality, integrity, and availability of data-in-use are protected",
        "keywords": "data in use, memory protection"
    },
    {
        "csf_id": "PR.DS-11",
        "subcategory": "PR.DS-11",
        "function": "Protect",
        "category": "PR.DS",
        "name": "Data Backups",
        "text": "Backups of data are created, protected, maintained, and tested",
        "keywords": "backups, backup testing, data recovery"
    },
    # Platform Security (PR.PS)
    {
        "csf_id": "PR.PS-01",
        "subcategory": "PR.PS-01",
        "function": "Protect",
        "category": "PR.PS",
        "name": "Configuration Management",
        "text": "Configuration management practices are established and applied",
        "keywords": "configuration management, baseline, hardening"
    },
    {
        "csf_id": "PR.PS-02",
        "subcategory": "PR.PS-02",
        "function": "Protect",
        "category": "PR.PS",
        "name": "Software Maintenance",
        "text": "Software is maintained, replaced, and removed commensurate with risk",
        "keywords": "patch management, software updates, EOL"
    },
    {
        "csf_id": "PR.PS-03",
        "subcategory": "PR.PS-03",
        "function": "Protect",
        "category": "PR.PS",
        "name": "Hardware Maintenance",
        "text": "Hardware is maintained, replaced, and removed commensurate with risk",
        "keywords": "hardware maintenance, asset disposal"
    },
    {
        "csf_id": "PR.PS-04",
        "subcategory": "PR.PS-04",
        "function": "Protect",
        "category": "PR.PS",
        "name": "Log Management",
        "text": "Log records are generated and made available for continuous monitoring",
        "keywords": "logging, audit logs, log retention"
    },
    {
        "csf_id": "PR.PS-05",
        "subcategory": "PR.PS-05",
        "function": "Protect",
        "category": "PR.PS",
        "name": "Software Execution Prevention",
        "text": "Installation and execution of unauthorized software are prevented",
        "keywords": "application whitelisting, software restriction"
    },
    {
        "csf_id": "PR.PS-06",
        "subcategory": "PR.PS-06",
        "function": "Protect",
        "category": "PR.PS",
        "name": "Secure Software Development",
        "text": "Secure software development practices are integrated, and their performance is monitored throughout the software development life cycle",
        "keywords": "secure SDLC, DevSecOps, secure coding"
    },
    # Technology Infrastructure Resilience (PR.IR)
    {
        "csf_id": "PR.IR-01",
        "subcategory": "PR.IR-01",
        "function": "Protect",
        "category": "PR.IR",
        "name": "Network Protection",
        "text": "Networks and environments are protected from unauthorized logical access and usage",
        "keywords": "network security, firewall, segmentation"
    },
    {
        "csf_id": "PR.IR-02",
        "subcategory": "PR.IR-02",
        "function": "Protect",
        "category": "PR.IR",
        "name": "Environmental Protection",
        "text": "The organization's technology assets are protected from environmental threats",
        "keywords": "environmental controls, physical security"
    },
    {
        "csf_id": "PR.IR-03",
        "subcategory": "PR.IR-03",
        "function": "Protect",
        "category": "PR.IR",
        "name": "Resilience Mechanisms",
        "text": "Mechanisms are implemented to achieve resilience requirements in normal and adverse situations",
        "keywords": "resilience, redundancy, fault tolerance"
    },
    {
        "csf_id": "PR.IR-04",
        "subcategory": "PR.IR-04",
        "function": "Protect",
        "category": "PR.IR",
        "name": "Resource Capacity",
        "text": "Adequate resource capacity to ensure availability is maintained",
        "keywords": "capacity planning, availability, scalability"
    },
    
    # DETECT (DE) - 11 Subcategories
    # Continuous Monitoring (DE.CM)
    {
        "csf_id": "DE.CM-01",
        "subcategory": "DE.CM-01",
        "function": "Detect",
        "category": "DE.CM",
        "name": "Network Monitoring",
        "text": "Networks and network services are monitored to find potentially adverse events",
        "keywords": "network monitoring, IDS, IPS"
    },
    {
        "csf_id": "DE.CM-02",
        "subcategory": "DE.CM-02",
        "function": "Detect",
        "category": "DE.CM",
        "name": "Physical Environment Monitoring",
        "text": "The physical environment is monitored to find potentially adverse events",
        "keywords": "physical monitoring, surveillance"
    },
    {
        "csf_id": "DE.CM-03",
        "subcategory": "DE.CM-03",
        "function": "Detect",
        "category": "DE.CM",
        "name": "Personnel Activity Monitoring",
        "text": "Personnel activity and technology usage are monitored to find potentially adverse events",
        "keywords": "user behavior monitoring, insider threat"
    },
    {
        "csf_id": "DE.CM-06",
        "subcategory": "DE.CM-06",
        "function": "Detect",
        "category": "DE.CM",
        "name": "External Service Provider Monitoring",
        "text": "External service provider activities and services are monitored to find potentially adverse events",
        "keywords": "third party monitoring, supplier monitoring"
    },
    {
        "csf_id": "DE.CM-09",
        "subcategory": "DE.CM-09",
        "function": "Detect",
        "category": "DE.CM",
        "name": "Computing Resource Monitoring",
        "text": "Computing hardware and software, runtime environments, and their data are monitored to find potentially adverse events",
        "keywords": "endpoint monitoring, system monitoring, EDR"
    },
    # Adverse Event Analysis (DE.AE)
    {
        "csf_id": "DE.AE-02",
        "subcategory": "DE.AE-02",
        "function": "Detect",
        "category": "DE.AE",
        "name": "Event Analysis",
        "text": "Potentially adverse events are analyzed to better understand associated activities",
        "keywords": "event analysis, security analysis"
    },
    {
        "csf_id": "DE.AE-03",
        "subcategory": "DE.AE-03",
        "function": "Detect",
        "category": "DE.AE",
        "name": "Information Correlation",
        "text": "Information is correlated from multiple sources",
        "keywords": "correlation, SIEM, log aggregation"
    },
    {
        "csf_id": "DE.AE-04",
        "subcategory": "DE.AE-04",
        "function": "Detect",
        "category": "DE.AE",
        "name": "Impact Estimation",
        "text": "The estimated impact and scope of adverse events are understood",
        "keywords": "impact assessment, scope analysis"
    },
    {
        "csf_id": "DE.AE-06",
        "subcategory": "DE.AE-06",
        "function": "Detect",
        "category": "DE.AE",
        "name": "Event Information Sharing",
        "text": "Information on adverse events is provided to authorized staff and tools",
        "keywords": "alerting, notification, escalation"
    },
    {
        "csf_id": "DE.AE-07",
        "subcategory": "DE.AE-07",
        "function": "Detect",
        "category": "DE.AE",
        "name": "Threat Intelligence Integration",
        "text": "Cyber threat intelligence and other contextual information are integrated into the analysis",
        "keywords": "threat intelligence, context, indicators"
    },
    {
        "csf_id": "DE.AE-08",
        "subcategory": "DE.AE-08",
        "function": "Detect",
        "category": "DE.AE",
        "name": "Incident Declaration",
        "text": "Incidents are declared when adverse events meet the defined incident criteria",
        "keywords": "incident declaration, incident criteria"
    },
    
    # RESPOND (RS) - 13 Subcategories
    # Incident Management (RS.MA)
    {
        "csf_id": "RS.MA-01",
        "subcategory": "RS.MA-01",
        "function": "Respond",
        "category": "RS.MA",
        "name": "Incident Response Plan Execution",
        "text": "The incident response plan is executed in coordination with relevant third parties once an incident is declared",
        "keywords": "incident response, IR plan"
    },
    {
        "csf_id": "RS.MA-02",
        "subcategory": "RS.MA-02",
        "function": "Respond",
        "category": "RS.MA",
        "name": "Incident Report Triage",
        "text": "Incident reports are triaged and validated",
        "keywords": "triage, incident validation"
    },
    {
        "csf_id": "RS.MA-03",
        "subcategory": "RS.MA-03",
        "function": "Respond",
        "category": "RS.MA",
        "name": "Incident Categorization",
        "text": "Incidents are categorized and prioritized",
        "keywords": "categorization, prioritization, severity"
    },
    {
        "csf_id": "RS.MA-04",
        "subcategory": "RS.MA-04",
        "function": "Respond",
        "category": "RS.MA",
        "name": "Incident Escalation",
        "text": "Incidents are escalated or elevated as needed",
        "keywords": "escalation, elevation"
    },
    {
        "csf_id": "RS.MA-05",
        "subcategory": "RS.MA-05",
        "function": "Respond",
        "category": "RS.MA",
        "name": "Recovery Initiation",
        "text": "The criteria for initiating incident recovery are applied",
        "keywords": "recovery criteria, recovery transition"
    },
    # Incident Analysis (RS.AN)
    {
        "csf_id": "RS.AN-03",
        "subcategory": "RS.AN-03",
        "function": "Respond",
        "category": "RS.AN",
        "name": "Root Cause Analysis",
        "text": "Analysis is performed to establish what has taken place during an incident and the root cause of the incident",
        "keywords": "root cause analysis, forensics, investigation"
    },
    {
        "csf_id": "RS.AN-06",
        "subcategory": "RS.AN-06",
        "function": "Respond",
        "category": "RS.AN",
        "name": "Investigation Records",
        "text": "Actions performed during an investigation are recorded, and the records' integrity and provenance are preserved",
        "keywords": "chain of custody, forensic evidence"
    },
    {
        "csf_id": "RS.AN-07",
        "subcategory": "RS.AN-07",
        "function": "Respond",
        "category": "RS.AN",
        "name": "Incident Data Collection",
        "text": "Incident data and metadata are collected, and their integrity and provenance are preserved",
        "keywords": "evidence collection, data preservation"
    },
    {
        "csf_id": "RS.AN-08",
        "subcategory": "RS.AN-08",
        "function": "Respond",
        "category": "RS.AN",
        "name": "Incident Magnitude",
        "text": "An incident's magnitude is estimated and validated",
        "keywords": "impact assessment, magnitude"
    },
    # Incident Response Reporting and Communication (RS.CO)
    {
        "csf_id": "RS.CO-02",
        "subcategory": "RS.CO-02",
        "function": "Respond",
        "category": "RS.CO",
        "name": "Stakeholder Notification",
        "text": "Internal and external stakeholders are notified of incidents",
        "keywords": "notification, stakeholder communication"
    },
    {
        "csf_id": "RS.CO-03",
        "subcategory": "RS.CO-03",
        "function": "Respond",
        "category": "RS.CO",
        "name": "Information Sharing",
        "text": "Information is shared with designated internal and external stakeholders",
        "keywords": "information sharing, coordination"
    },
    # Incident Mitigation (RS.MI)
    {
        "csf_id": "RS.MI-01",
        "subcategory": "RS.MI-01",
        "function": "Respond",
        "category": "RS.MI",
        "name": "Incident Containment",
        "text": "Incidents are contained",
        "keywords": "containment, isolation"
    },
    {
        "csf_id": "RS.MI-02",
        "subcategory": "RS.MI-02",
        "function": "Respond",
        "category": "RS.MI",
        "name": "Incident Eradication",
        "text": "Incidents are eradicated",
        "keywords": "eradication, removal, remediation"
    },
    
    # RECOVER (RC) - 8 Subcategories
    # Incident Recovery Plan Execution (RC.RP)
    {
        "csf_id": "RC.RP-01",
        "subcategory": "RC.RP-01",
        "function": "Recover",
        "category": "RC.RP",
        "name": "Recovery Plan Execution",
        "text": "The recovery portion of the incident response plan is executed once initiated from the incident response process",
        "keywords": "recovery plan, disaster recovery"
    },
    {
        "csf_id": "RC.RP-02",
        "subcategory": "RC.RP-02",
        "function": "Recover",
        "category": "RC.RP",
        "name": "Recovery Action Selection",
        "text": "Recovery actions are selected, scoped, prioritized, and performed",
        "keywords": "recovery actions, restoration"
    },
    {
        "csf_id": "RC.RP-03",
        "subcategory": "RC.RP-03",
        "function": "Recover",
        "category": "RC.RP",
        "name": "Backup Integrity Verification",
        "text": "The integrity of backups and other restoration assets is verified before using them for restoration",
        "keywords": "backup verification, backup integrity"
    },
    {
        "csf_id": "RC.RP-04",
        "subcategory": "RC.RP-04",
        "function": "Recover",
        "category": "RC.RP",
        "name": "Post-Incident Operations",
        "text": "Critical mission functions and cybersecurity risk management are considered to establish post-incident operational norms",
        "keywords": "operational norms, mission functions"
    },
    {
        "csf_id": "RC.RP-05",
        "subcategory": "RC.RP-05",
        "function": "Recover",
        "category": "RC.RP",
        "name": "Service Restoration",
        "text": "The integrity of restored assets is verified, systems and services are restored, and normal operating status is confirmed",
        "keywords": "restoration, service recovery, verification"
    },
    {
        "csf_id": "RC.RP-06",
        "subcategory": "RC.RP-06",
        "function": "Recover",
        "category": "RC.RP",
        "name": "Recovery Completion",
        "text": "The end of incident recovery is declared based on criteria, and incident-related documentation is completed",
        "keywords": "recovery completion, post-incident review"
    },
    # Incident Recovery Communication (RC.CO)
    {
        "csf_id": "RC.CO-03",
        "subcategory": "RC.CO-03",
        "function": "Recover",
        "category": "RC.CO",
        "name": "Recovery Progress Communication",
        "text": "Recovery activities and progress in restoring operational capabilities are communicated to designated internal and external stakeholders",
        "keywords": "recovery communication, status updates"
    },
    {
        "csf_id": "RC.CO-04",
        "subcategory": "RC.CO-04",
        "function": "Recover",
        "category": "RC.CO",
        "name": "Public Updates",
        "text": "Public updates on incident recovery are shared using approved methods and messaging",
        "keywords": "public communication, messaging"
    },
]


def seed_controls():
    """Seed the database with NIST CSF 2.0 controls."""
    print(f"Seeding {len(CSF_CONTROLS)} NIST CSF 2.0 controls...")

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
        
        print(f"\nTotal: {len(CSF_CONTROLS)} subcategories")


if __name__ == "__main__":
    seed_controls()
