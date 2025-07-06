import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import logging

def generate_analysis_pdf(analysis_data, output_path, language='en'):
    """
    Generate a comprehensive professional PDF report from advanced analysis data
    """
    try:
        # Create document with larger page size for comprehensive content
        doc = SimpleDocTemplate(output_path, pagesize=A4, 
                              leftMargin=0.75*inch, rightMargin=0.75*inch,
                              topMargin=1*inch, bottomMargin=1*inch)
        styles = getSampleStyleSheet()
        
        # Enhanced custom styles for comprehensive report
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=26,
            textColor=HexColor('#1a252f'),
            spaceAfter=30,
            alignment=1,  # Center alignment
            fontName='Helvetica-Bold'
        )
        
        executive_style = ParagraphStyle(
            'ExecutiveSummary',
            parent=styles['Normal'],
            fontSize=13,
            textColor=HexColor('#2c3e50'),
            spaceAfter=20,
            spaceBefore=15,
            fontName='Helvetica-Oblique',
            leftIndent=20,
            rightIndent=20,
            backColor=HexColor('#f8f9fa'),
            borderWidth=0.5,
            borderColor=HexColor('#dee2e6'),
            borderPadding=10
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#2c3e50'),
            spaceAfter=15,
            spaceBefore=25,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderColor=HexColor('#3498db'),
            borderPadding=0
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#34495e'),
            spaceAfter=10,
            spaceBefore=15,
            fontName='Helvetica-Bold'
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#2c3e50'),
            spaceAfter=8,
            leading=14
        )
        
        # Build comprehensive content
        content = []
        
        # Title and Header
        content.append(Paragraph("Comprehensive Life Path & Face Analysis Report", title_style))
        content.append(Spacer(1, 20))
        
        # Handle error case
        if 'error' in analysis_data:
            content.append(Paragraph("Analysis Error", heading_style))
            content.append(Paragraph(analysis_data.get('message', 'Unknown error occurred'), body_style))
            doc.build(content)
            return
        
        # Executive Summary
        if 'executive_summary' in analysis_data:
            content.append(Paragraph("Executive Summary", heading_style))
            content.append(Paragraph(analysis_data['executive_summary'], executive_style))
            content.append(Spacer(1, 15))
        
        # 1. Personality Core
        if 'personality_core' in analysis_data:
            content.append(Paragraph("1. Core Personality Profile", heading_style))
            personality = analysis_data['personality_core']
            
            for key, value in personality.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(f"<b>{title}:</b> {value}", body_style))
                    content.append(Spacer(1, 8))
            content.append(PageBreak())
        
        # 2. Life Path Analysis
        if 'life_path_analysis' in analysis_data:
            content.append(Paragraph("2. Life Path & Destiny Analysis", heading_style))
            life_path = analysis_data['life_path_analysis']
            
            for key, value in life_path.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(title, subheading_style))
                    content.append(Paragraph(str(value), body_style))
                    content.append(Spacer(1, 10))
            content.append(PageBreak())
        
        # 3. Professional Guidance
        if 'professional_guidance' in analysis_data:
            content.append(Paragraph("3. Career & Professional Development", heading_style))
            professional = analysis_data['professional_guidance']
            
            for key, value in professional.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(title, subheading_style))
                    content.append(Paragraph(str(value), body_style))
                    content.append(Spacer(1, 10))
            content.append(PageBreak())
        
        # 4. Relationship Insights
        if 'relationship_insights' in analysis_data:
            content.append(Paragraph("4. Relationships & Social Dynamics", heading_style))
            relationships = analysis_data['relationship_insights']
            
            for key, value in relationships.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(title, subheading_style))
                    content.append(Paragraph(str(value), body_style))
                    content.append(Spacer(1, 10))
            content.append(PageBreak())
        
        # 5. Health & Vitality
        if 'health_vitality' in analysis_data:
            content.append(Paragraph("5. Health, Vitality & Wellness", heading_style))
            health = analysis_data['health_vitality']
            
            for key, value in health.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(title, subheading_style))
                    content.append(Paragraph(str(value), body_style))
                    content.append(Spacer(1, 10))
            content.append(PageBreak())
        
        # 6. Wealth & Abundance
        if 'wealth_abundance' in analysis_data:
            content.append(Paragraph("6. Financial Patterns & Wealth Building", heading_style))
            wealth = analysis_data['wealth_abundance']
            
            for key, value in wealth.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(title, subheading_style))
                    content.append(Paragraph(str(value), body_style))
                    content.append(Spacer(1, 10))
            content.append(PageBreak())
        
        # 7. Personal Development
        if 'personal_development' in analysis_data:
            content.append(Paragraph("7. Personal Growth & Development", heading_style))
            development = analysis_data['personal_development']
            
            for key, value in development.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(title, subheading_style))
                    content.append(Paragraph(str(value), body_style))
                    content.append(Spacer(1, 10))
            content.append(PageBreak())
        
        # 8. Action Plan
        if 'action_plan' in analysis_data:
            content.append(Paragraph("8. Strategic Action Plan", heading_style))
            action_plan = analysis_data['action_plan']
            
            for key, value in action_plan.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(title, subheading_style))
                    content.append(Paragraph(str(value), body_style))
                    content.append(Spacer(1, 10))
            content.append(PageBreak())
        
        # 9. Advanced Insights
        if 'advanced_insights' in analysis_data:
            content.append(Paragraph("9. Advanced Insights & Hidden Potentials", heading_style))
            advanced = analysis_data['advanced_insights']
            
            for key, value in advanced.items():
                if value:
                    title = key.replace('_', ' ').title()
                    content.append(Paragraph(title, subheading_style))
                    content.append(Paragraph(str(value), body_style))
                    content.append(Spacer(1, 10))
            
            content.append(Spacer(1, 20))
        
        # Footer with disclaimer
        content.append(Spacer(1, 30))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#7f8c8d'),
            alignment=1,
            spaceAfter=10,
            fontName='Helvetica-Oblique'
        )
        
        content.append(Paragraph(
            "This comprehensive analysis combines traditional physiognomy with modern psychological profiling. "
            "Results are for personal development and entertainment purposes. Individual experiences may vary.",
            disclaimer_style
        ))
        
        content.append(Paragraph(
            f"Report generated for facesecrets.ai - Your personal development companion",
            disclaimer_style
        ))
        
        # Build PDF
        doc.build(content)
        logging.info(f"PDF generated successfully: {output_path}")
        
    except Exception as e:
        logging.error(f"PDF generation error: {e}")
        # Create a simple error PDF
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        content = [
            Paragraph("PDF Generation Error", styles['Title']),
            Paragraph("Unable to generate your analysis report. Please try again.", styles['Normal'])
        ]
        doc.build(content)
