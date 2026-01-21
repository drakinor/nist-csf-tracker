"""
PDF Report Generation Service for NIST CSF Tracker

EPIC 8: PDF Reporting
- Executive summary generation
- Compliance report with evidence index
- Gap analysis report
- Action plan export
- Custom branding/templates
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
from io import BytesIO
from typing import List, Dict, Any, Optional
from sqlmodel import Session, select
from app.models import Control, Evidence, Score, Gap, Action, Risk


class PDFReportService:
    """Service for generating PDF reports with ReportLab."""
    
    def __init__(self, session: Session):
        self.session = session
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Set up custom paragraph styles for reports."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=20,
            alignment=TA_CENTER
        ))
        
        # Section heading
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#1e40af'),
            spaceAfter=12,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Subsection heading
        self.styles.add(ParagraphStyle(
            name='SubsectionHeading',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#374151'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        ))
        
        # Body text
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.black,
            spaceAfter=6,
            alignment=TA_JUSTIFY
        ))
        
        # Small text
        self.styles.add(ParagraphStyle(
            name='SmallText',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#6b7280'),
            spaceAfter=4
        ))
    
    def _add_header_footer(self, canvas, doc):
        """Add header and footer to each page."""
        canvas.saveState()
        
        # Footer
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6b7280'))
        canvas.drawString(
            inch,
            0.5 * inch,
            f"NIST CSF Tracker Report - Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        )
        canvas.drawRightString(
            doc.pagesize[0] - inch,
            0.5 * inch,
            f"Page {canvas.getPageNumber()}"
        )
        
        canvas.restoreState()
    
    def generate_executive_summary(self, organization_name: str = "Organization") -> BytesIO:
        """
        Generate an executive summary PDF report.
        
        Includes:
        - Overall compliance percentage
        - Function-level breakdown
        - Top gaps and risks
        - Key statistics
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph(
            "NIST Cybersecurity Framework",
            self.styles['ReportTitle']
        ))
        story.append(Paragraph(
            "Executive Summary Report",
            self.styles['ReportTitle']
        ))
        story.append(Paragraph(
            f"{organization_name}<br/>{datetime.now().strftime('%B %d, %Y')}",
            self.styles['ReportSubtitle']
        ))
        story.append(Spacer(1, 0.5 * inch))
        
        # Get data
        controls = list(self.session.exec(select(Control)).all())
        scores = list(self.session.exec(select(Score)).all())
        gaps = list(self.session.exec(select(Gap)).all())
        risks = list(self.session.exec(select(Risk)).all())
        
        # Calculate overall compliance
        score_map = {s.control_id: s.score_value for s in scores}
        total_score = sum(score_map.values())
        max_score = len(controls) * 1.0
        compliance_pct = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Overall Status Section
        story.append(Paragraph("Overall Compliance Status", self.styles['SectionHeading']))
        
        status_data = [
            ['Metric', 'Value'],
            ['Overall Compliance', f"{compliance_pct:.1f}%"],
            ['Total Controls', str(len(controls))],
            ['Fully Implemented', str(sum(1 for s in scores if s.score_value >= 1.0))],
            ['Partially Implemented', str(sum(1 for s in scores if 0 < s.score_value < 1.0))],
            ['Not Implemented', str(sum(1 for s in scores if s.score_value == 0.0))],
            ['Open Gaps', str(len([g for g in gaps if g.status == 'open']))],
            ['Active Risks', str(len([r for r in risks if r.status == 'open']))],
        ]
        
        status_table = Table(status_data, colWidths=[3 * inch, 2 * inch])
        status_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ]))
        story.append(status_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Function Breakdown
        story.append(Paragraph("Compliance by Function", self.styles['SectionHeading']))
        
        functions = {}
        for control in controls:
            if control.function not in functions:
                functions[control.function] = {'controls': [], 'scores': []}
            functions[control.function]['controls'].append(control)
            if control.id in score_map:
                functions[control.function]['scores'].append(score_map[control.id])
        
        function_data = [['Function', 'Controls', 'Avg Score', 'Compliance %']]
        for func_name in sorted(functions.keys()):
            func_controls = functions[func_name]['controls']
            func_scores = functions[func_name]['scores']
            avg_score = sum(func_scores) / len(func_scores) if func_scores else 0
            compliance = avg_score * 100
            
            function_data.append([
                func_name,
                str(len(func_controls)),
                f"{avg_score:.2f}",
                f"{compliance:.1f}%"
            ])
        
        function_table = Table(function_data, colWidths=[2.5 * inch, 1 * inch, 1 * inch, 1.5 * inch])
        function_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ]))
        story.append(function_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Critical Gaps
        critical_gaps = [g for g in gaps if g.severity in ['critical', 'high'] and g.status == 'open']
        if critical_gaps:
            story.append(Paragraph("Critical & High Priority Gaps", self.styles['SectionHeading']))
            story.append(Paragraph(
                f"The following {len(critical_gaps)} gaps require immediate attention:",
                self.styles['BodyText']
            ))
            story.append(Spacer(1, 0.1 * inch))
            
            for gap in critical_gaps[:10]:  # Limit to top 10
                control = self.session.get(Control, gap.control_id)
                gap_text = f"<b>[{gap.severity.upper()}]</b> {control.csf_id} - {control.name}: {gap.description}"
                story.append(Paragraph(gap_text, self.styles['BodyText']))
                story.append(Spacer(1, 0.05 * inch))
        
        story.append(PageBreak())
        
        # Recommendations
        story.append(Paragraph("Recommendations", self.styles['SectionHeading']))
        
        recommendations = []
        if compliance_pct < 50:
            recommendations.append("Focus on implementing baseline controls across all functions to achieve foundational compliance.")
        if critical_gaps:
            recommendations.append(f"Address {len(critical_gaps)} critical/high priority gaps as immediate priorities.")
        if len([r for r in risks if r.status == 'open']) > 10:
            recommendations.append("Conduct comprehensive risk assessment and develop mitigation strategies for open risks.")
        recommendations.append("Establish regular review cycles for accepted risks and implemented controls.")
        recommendations.append("Continue evidence collection and validation to improve scoring accuracy.")
        
        for rec in recommendations:
            story.append(Paragraph(f"• {rec}", self.styles['BodyText']))
            story.append(Spacer(1, 0.1 * inch))
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        buffer.seek(0)
        return buffer
    
    def generate_compliance_report(self, organization_name: str = "Organization") -> BytesIO:
        """
        Generate a detailed compliance report with evidence index.
        
        Includes:
        - Control-by-control status
        - Evidence details
        - Scoring rationales
        - Evidence artifact references
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            "NIST CSF Compliance Report",
            self.styles['ReportTitle']
        ))
        story.append(Paragraph(
            f"{organization_name}<br/>{datetime.now().strftime('%B %d, %Y')}",
            self.styles['ReportSubtitle']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Get all controls with scores
        controls = list(self.session.exec(select(Control)).all())
        scores = {s.control_id: s for s in self.session.exec(select(Score)).all()}
        
        # Group by function
        functions = {}
        for control in controls:
            if control.function not in functions:
                functions[control.function] = []
            functions[control.function].append(control)
        
        # Generate control details by function
        for func_name in sorted(functions.keys()):
            story.append(Paragraph(f"Function: {func_name}", self.styles['SectionHeading']))
            
            for control in sorted(functions[func_name], key=lambda c: c.csf_id):
                # Control header
                control_title = f"{control.csf_id}: {control.name}"
                story.append(Paragraph(control_title, self.styles['SubsectionHeading']))
                
                # Control description
                story.append(Paragraph(f"<i>{control.description}</i>", self.styles['BodyText']))
                story.append(Spacer(1, 0.05 * inch))
                
                # Score and status
                score = scores.get(control.id)
                if score:
                    score_color = self._get_score_color(score.score_value)
                    score_text = f"<b>Score:</b> {score.score_value:.2f} / 1.00 ({score.score_value * 100:.0f}%)"
                    story.append(Paragraph(score_text, self.styles['BodyText']))
                    story.append(Paragraph(f"<b>Method:</b> {score.method}", self.styles['SmallText']))
                    story.append(Paragraph(f"<b>Rationale:</b> {score.score_rationale}", self.styles['SmallText']))
                else:
                    story.append(Paragraph("<b>Score:</b> Not yet scored", self.styles['BodyText']))
                
                story.append(Spacer(1, 0.1 * inch))
                
                # Evidence
                evidence_list = list(self.session.exec(
                    select(Evidence).where(Evidence.control_id == control.id, Evidence.status == "validated")
                ).all())
                
                if evidence_list:
                    story.append(Paragraph(f"<b>Evidence ({len(evidence_list)} items):</b>", self.styles['BodyText']))
                    
                    for ev in evidence_list:
                        ev_text = f"• [{ev.evidence_type}] {ev.artifact_name}"
                        if ev.locator:
                            ev_text += f" (Page {ev.locator})"
                        story.append(Paragraph(ev_text, self.styles['SmallText']))
                else:
                    story.append(Paragraph("<i>No validated evidence</i>", self.styles['SmallText']))
                
                story.append(Spacer(1, 0.2 * inch))
            
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        buffer.seek(0)
        return buffer
    
    def generate_gap_analysis_report(self, organization_name: str = "Organization") -> BytesIO:
        """
        Generate a gap analysis report.
        
        Includes:
        - All identified gaps by severity
        - Gap descriptions and recommendations
        - Associated controls
        - Remediation priorities
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            "Gap Analysis Report",
            self.styles['ReportTitle']
        ))
        story.append(Paragraph(
            f"{organization_name}<br/>{datetime.now().strftime('%B %d, %Y')}",
            self.styles['ReportSubtitle']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Get all gaps
        gaps = list(self.session.exec(select(Gap)).all())
        
        # Summary
        story.append(Paragraph("Gap Summary", self.styles['SectionHeading']))
        
        gap_summary = [
            ['Severity', 'Open', 'In Progress', 'Resolved', 'Total'],
        ]
        
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_gaps = [g for g in gaps if g.severity == severity]
            open_count = len([g for g in severity_gaps if g.status == 'open'])
            in_progress = len([g for g in severity_gaps if g.status == 'in_progress'])
            resolved = len([g for g in severity_gaps if g.status == 'resolved'])
            total = len(severity_gaps)
            
            gap_summary.append([
                severity.capitalize(),
                str(open_count),
                str(in_progress),
                str(resolved),
                str(total)
            ])
        
        summary_table = Table(gap_summary, colWidths=[1.5 * inch, 1 * inch, 1.2 * inch, 1 * inch, 1 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Detailed gaps by severity
        for severity in ['critical', 'high', 'medium', 'low']:
            severity_gaps = [g for g in gaps if g.severity == severity and g.status in ['open', 'in_progress']]
            
            if not severity_gaps:
                continue
            
            story.append(Paragraph(
                f"{severity.capitalize()} Priority Gaps ({len(severity_gaps)})",
                self.styles['SectionHeading']
            ))
            
            for gap in severity_gaps:
                control = self.session.get(Control, gap.control_id)
                
                # Gap header
                gap_title = f"{control.csf_id} - {control.name}"
                story.append(Paragraph(gap_title, self.styles['SubsectionHeading']))
                
                # Gap details
                story.append(Paragraph(f"<b>Type:</b> {gap.gap_type.replace('_', ' ').title()}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Status:</b> {gap.status.replace('_', ' ').title()}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Description:</b> {gap.description}", self.styles['BodyText']))
                
                if gap.recommendation:
                    story.append(Paragraph(f"<b>Recommendation:</b> {gap.recommendation}", self.styles['BodyText']))
                
                story.append(Spacer(1, 0.15 * inch))
            
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        buffer.seek(0)
        return buffer
    
    def generate_action_plan_report(self, organization_name: str = "Organization") -> BytesIO:
        """
        Generate an action plan report.
        
        Includes:
        - All open and in-progress actions
        - Priorities and due dates
        - Assignment and status
        - Related gaps
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        story = []
        
        # Title
        story.append(Paragraph(
            "Action Plan Report",
            self.styles['ReportTitle']
        ))
        story.append(Paragraph(
            f"{organization_name}<br/>{datetime.now().strftime('%B %d, %Y')}",
            self.styles['ReportSubtitle']
        ))
        story.append(Spacer(1, 0.3 * inch))
        
        # Get all actions
        actions = list(self.session.exec(select(Action)).all())
        
        # Summary
        story.append(Paragraph("Action Summary", self.styles['SectionHeading']))
        
        action_summary = [
            ['Priority', 'Open', 'In Progress', 'Completed', 'Total'],
        ]
        
        for priority in ['critical', 'high', 'medium', 'low']:
            priority_actions = [a for a in actions if a.priority == priority]
            open_count = len([a for a in priority_actions if a.status == 'open'])
            in_progress = len([a for a in priority_actions if a.status == 'in_progress'])
            completed = len([a for a in priority_actions if a.status == 'completed'])
            total = len(priority_actions)
            
            action_summary.append([
                priority.capitalize(),
                str(open_count),
                str(in_progress),
                str(completed),
                str(total)
            ])
        
        summary_table = Table(action_summary, colWidths=[1.5 * inch, 1 * inch, 1.2 * inch, 1.2 * inch, 1 * inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f3f4f6')]),
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3 * inch))
        
        # Detailed actions by priority
        for priority in ['critical', 'high', 'medium', 'low']:
            priority_actions = [a for a in actions if a.priority == priority and a.status != 'completed']
            
            if not priority_actions:
                continue
            
            story.append(Paragraph(
                f"{priority.capitalize()} Priority Actions ({len(priority_actions)})",
                self.styles['SectionHeading']
            ))
            
            for action in sorted(priority_actions, key=lambda a: a.due_date if a.due_date else datetime.max):
                # Action header
                story.append(Paragraph(action.title, self.styles['SubsectionHeading']))
                
                # Action details
                story.append(Paragraph(f"<b>Status:</b> {action.status.replace('_', ' ').title()}", self.styles['BodyText']))
                if action.assigned_to:
                    story.append(Paragraph(f"<b>Assigned To:</b> {action.assigned_to}", self.styles['BodyText']))
                if action.due_date:
                    story.append(Paragraph(f"<b>Due Date:</b> {action.due_date.strftime('%Y-%m-%d')}", self.styles['BodyText']))
                story.append(Paragraph(f"<b>Description:</b> {action.description}", self.styles['BodyText']))
                
                # Check acceptance criteria
                if action.acceptance_criteria:
                    story.append(Paragraph(f"<b>Acceptance Criteria:</b> {action.acceptance_criteria}", self.styles['SmallText']))
                
                story.append(Spacer(1, 0.15 * inch))
            
            story.append(PageBreak())
        
        # Build PDF
        doc.build(story, onFirstPage=self._add_header_footer, onLaterPages=self._add_header_footer)
        buffer.seek(0)
        return buffer
    
    def _get_score_color(self, score: float) -> colors.Color:
        """Get color for score visualization."""
        if score >= 1.0:
            return colors.HexColor('#10b981')  # green
        elif score >= 0.66:
            return colors.HexColor('#3b82f6')  # blue
        elif score >= 0.33:
            return colors.HexColor('#f59e0b')  # amber
        else:
            return colors.HexColor('#dc2626')  # red
