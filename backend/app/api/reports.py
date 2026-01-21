"""
PDF Report Generation API

EPIC 8: PDF Reporting endpoints
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from app.database import get_session
from app.services.pdf_service import PDFReportService
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/executive-summary")
def generate_executive_summary(
    organization: str = Query("Organization", description="Organization name for report"),
    session: Session = Depends(get_session)
):
    """
    Generate an executive summary PDF report.
    
    **Includes:**
    - Overall compliance percentage
    - Function-level breakdown
    - Critical gaps summary
    - Key statistics
    - Recommendations
    
    **Returns:** PDF file as downloadable attachment
    """
    pdf_service = PDFReportService(session)
    pdf_buffer = pdf_service.generate_executive_summary(organization)
    
    filename = f"NIST_CSF_Executive_Summary_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/compliance")
def generate_compliance_report(
    organization: str = Query("Organization", description="Organization name for report"),
    session: Session = Depends(get_session)
):
    """
    Generate a detailed compliance report PDF with evidence index.
    
    **Includes:**
    - Control-by-control status
    - Evidence details and artifact references
    - Scoring rationales
    - Implementation details
    
    **Returns:** PDF file as downloadable attachment
    """
    pdf_service = PDFReportService(session)
    pdf_buffer = pdf_service.generate_compliance_report(organization)
    
    filename = f"NIST_CSF_Compliance_Report_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/gap-analysis")
def generate_gap_analysis_report(
    organization: str = Query("Organization", description="Organization name for report"),
    session: Session = Depends(get_session)
):
    """
    Generate a gap analysis PDF report.
    
    **Includes:**
    - All identified gaps by severity
    - Gap descriptions and recommendations
    - Associated controls
    - Remediation priorities
    
    **Returns:** PDF file as downloadable attachment
    """
    pdf_service = PDFReportService(session)
    pdf_buffer = pdf_service.generate_gap_analysis_report(organization)
    
    filename = f"NIST_CSF_Gap_Analysis_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/action-plan")
def generate_action_plan_report(
    organization: str = Query("Organization", description="Organization name for report"),
    session: Session = Depends(get_session)
):
    """
    Generate an action plan PDF report.
    
    **Includes:**
    - All open and in-progress actions
    - Priorities and due dates
    - Assignment and status
    - Related gaps
    
    **Returns:** PDF file as downloadable attachment
    """
    pdf_service = PDFReportService(session)
    pdf_buffer = pdf_service.generate_action_plan_report(organization)
    
    filename = f"NIST_CSF_Action_Plan_{datetime.now().strftime('%Y%m%d')}.pdf"
    
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/available")
def list_available_reports():
    """
    List all available PDF report types.
    
    **Returns:** List of available report types with descriptions
    """
    return {
        "reports": [
            {
                "id": "executive-summary",
                "name": "Executive Summary",
                "description": "High-level overview with compliance metrics and key findings",
                "endpoint": "/api/reports/executive-summary"
            },
            {
                "id": "compliance",
                "name": "Compliance Report",
                "description": "Detailed control-by-control status with evidence index",
                "endpoint": "/api/reports/compliance"
            },
            {
                "id": "gap-analysis",
                "name": "Gap Analysis",
                "description": "Identified gaps by severity with remediation priorities",
                "endpoint": "/api/reports/gap-analysis"
            },
            {
                "id": "action-plan",
                "name": "Action Plan",
                "description": "Open and in-progress actions with assignments and due dates",
                "endpoint": "/api/reports/action-plan"
            }
        ]
    }
