import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

REPORTS_DIR = "/Users/shivam/Desktop/refinery_decision_system/refinery-simulator/reports"

def generate_pdf_report(run):
    """
    Generates a professional PDF report for a simulation run.
    Contains Scenario Information, Simulation Results, and AI Recommendations.
    """
    # Create reports directory if it doesn't exist
    if not os.path.exists(REPORTS_DIR):
        os.makedirs(REPORTS_DIR)
        
    filename = f"simulation_report_{run.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    file_path = os.path.join(REPORTS_DIR, filename)
    
    doc = SimpleDocTemplate(file_path, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    # Theme Palette (IBM Carbon style)
    primary_color = colors.HexColor("#0f62fe") # IBM Blue
    dark_neutral = colors.HexColor("#161616")  # Charcoal
    light_neutral = colors.HexColor("#f4f4f4") # Light Gray
    border_color = colors.HexColor("#e0e0e0")  # Hairline Gray
    
    # Styles
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=primary_color,
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=dark_neutral,
        spaceBefore=15,
        spaceAfter=8,
        borderColor=primary_color,
        borderWidth=1,
        borderRadius=0,
        borderPadding=5
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        textColor=dark_neutral,
        leading=14
    )
    
    body_bold_style = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )
    
    # --- Title Page Header ---
    story.append(Paragraph("Refinery Decision Intelligence System (RDIS)", title_style))
    story.append(Paragraph(f"<b>Simulation Run Report</b> | Run ID: #{run.id}", body_style))
    story.append(Paragraph(f"<b>Timestamp:</b> {run.run_timestamp.strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    story.append(Paragraph(f"<b>Operator Profile:</b> {run.user.username if run.user else 'System Operator'}", body_style))
    story.append(Spacer(1, 15))
    
    # --- Scenario Details ---
    story.append(Paragraph("Scenario Details", h2_style))
    scenario_info = [
        [Paragraph("<b>Scenario Name:</b>", body_style), Paragraph(run.scenario.name, body_style)],
        [Paragraph("<b>Scenario Type:</b>", body_style), Paragraph(run.scenario.type, body_style)],
        [Paragraph("<b>Description:</b>", body_style), Paragraph(run.scenario.description or "No description provided.", body_style)],
        [Paragraph("<b>Operational Risk Score:</b>", body_style), Paragraph(f"<b>{run.risk_score} / 100</b>", body_style)],
        [Paragraph("<b>Detected Bottleneck:</b>", body_style), Paragraph(run.bottleneck_unit.name if run.bottleneck_unit else "None", body_style)]
    ]
    t_scenario = Table(scenario_info, colWidths=[1.8 * inch, 5.2 * inch])
    t_scenario.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_neutral),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('BOX', (0,0), (-1,-1), 0.5, border_color),
    ]))
    story.append(t_scenario)
    story.append(Spacer(1, 15))
    
    # --- Simulation Results Table ---
    story.append(Paragraph("Operational Parameter Impact (Before vs After)", h2_style))
    
    results_headers = ["Unit Code", "Parameter", "Before State", "After State", "Change (%)"]
    results_data = [results_headers]
    
    for r in run.results:
        pct = 0.0
        if r.before_value != 0:
            pct = ((r.after_value - r.before_value) / r.before_value) * 100.0
            
        change_text = f"{r.after_value - r.before_value:+.2f} ({pct:+.1f}%)" if r.after_value != r.before_value else "0.00 (0.0%)"
        
        # Format values cleanly
        results_data.append([
            r.unit.code,
            r.parameter_name.capitalize(),
            f"{r.before_value:.2f}",
            f"{r.after_value:.2f}",
            change_text
        ])
        
    t_results = Table(results_data, colWidths=[1.2 * inch, 1.5 * inch, 1.3 * inch, 1.3 * inch, 1.7 * inch])
    t_results.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,-1), 9),
    ]))
    story.append(t_results)
    story.append(Spacer(1, 15))
    
    # --- AI Recommendations ---
    story.append(Paragraph("AI Recommendations & Decision Actions", h2_style))
    
    recs_data = []
    if not run.recommendations:
        recs_data.append([Paragraph("No operational risks detected. System working under nominal limits.", body_style)])
        t_recs = Table(recs_data, colWidths=[7.0 * inch])
        t_recs.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), light_neutral),
            ('BOX', (0,0), (-1,-1), 0.5, border_color),
            ('PADDING', (0,0), (-1,-1), 10),
        ]))
    else:
        for idx, rec in enumerate(run.recommendations):
            prio_color = "#da1e28" if rec.priority == 'High' else ("#f1c21b" if rec.priority == 'Medium' else "#0f62fe")
            prio_tag = f"<font color='{prio_color}'><b>[{rec.priority.upper()}]</b></font>"
            unit_tag = f"<b>{rec.unit.code}</b>: " if rec.unit else ""
            
            recs_data.append([
                Paragraph(f"{idx+1}.", body_bold_style),
                Paragraph(f"{prio_tag} {unit_tag}{rec.recommendation_text}", body_style)
            ])
            
        t_recs = Table(recs_data, colWidths=[0.3 * inch, 6.7 * inch])
        t_recs.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
            ('LINEBELOW', (0,0), (-1,-2), 0.5, border_color),
        ]))
        
    story.append(t_recs)
    
    # Build Document
    doc.build(story)
    return file_path
