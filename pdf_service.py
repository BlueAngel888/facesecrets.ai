import os
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import logging

def generate_analysis_pdf(analysis_data, output_path, language='en'):
    """
    Generate a professional PDF report from analysis data
    """
    try:
        # Create document
        doc = SimpleDocTemplate(output_path, pagesize=A4)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=HexColor('#34495e'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=HexColor('#7f8c8d'),
            spaceAfter=8,
            spaceBefore=12
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=11,
            textColor=HexColor('#2c3e50'),
            spaceAfter=8,
            leading=14
        )
        
        # Build content
        content = []
        
        # Title
        content.append(Paragraph("Ancient Wisdom Face Analysis Report", title_style))
        content.append(Spacer(1, 20))
        
        # Handle error case
        if 'error' in analysis_data:
            content.append(Paragraph("Analysis Error", heading_style))
            content.append(Paragraph(analysis_data.get('message', 'Unknown error occurred'), body_style))
            doc.build(content)
            return
        
        # Overall Personality
        if 'overall_personality' in analysis_data:
            content.append(Paragraph("Overall Personality Assessment", heading_style))
            content.append(Paragraph(analysis_data['overall_personality'], body_style))
            content.append(Spacer(1, 12))
        
        # Chinese Analysis
        if 'chinese_analysis' in analysis_data:
            content.append(Paragraph("Chinese Mian Xiang (Face Reading)", heading_style))
            chinese = analysis_data['chinese_analysis']
            
            for key, value in chinese.items():
                title = key.replace('_', ' ').title()
                content.append(Paragraph(title, subheading_style))
                content.append(Paragraph(str(value), body_style))
            
            content.append(PageBreak())
        
        # Greek Analysis  
        if 'greek_analysis' in analysis_data:
            content.append(Paragraph("Greek Physiognomy (Aristotelian)", heading_style))
            greek = analysis_data['greek_analysis']
            
            for key, value in greek.items():
                title = key.replace('_', ' ').title()
                content.append(Paragraph(title, subheading_style))
                content.append(Paragraph(str(value), body_style))
            
            content.append(Spacer(1, 20))
        
        # Vedic Analysis
        if 'vedic_analysis' in analysis_data:
            content.append(Paragraph("Vedic Samudrika Shastra", heading_style))
            vedic = analysis_data['vedic_analysis']
            
            for key, value in vedic.items():
                title = key.replace('_', ' ').title()
                content.append(Paragraph(title, subheading_style))
                content.append(Paragraph(str(value), body_style))
            
            content.append(PageBreak())
        
        # Islamic Analysis
        if 'islamic_analysis' in analysis_data:
            content.append(Paragraph("Islamic Firasa (Intuitive Reading)", heading_style))
            islamic = analysis_data['islamic_analysis']
            
            for key, value in islamic.items():
                title = key.replace('_', ' ').title()
                content.append(Paragraph(title, subheading_style))
                content.append(Paragraph(str(value), body_style))
            
            content.append(Spacer(1, 20))
        
        # Modern Analysis
        if 'modern_analysis' in analysis_data:
            content.append(Paragraph("Modern Analysis (FACS/Ekman)", heading_style))
            modern = analysis_data['modern_analysis']
            
            for key, value in modern.items():
                title = key.replace('_', ' ').title()
                content.append(Paragraph(title, subheading_style))
                content.append(Paragraph(str(value), body_style))
            
            content.append(PageBreak())
        
        # Life Predictions
        if 'life_predictions' in analysis_data:
            content.append(Paragraph("Life Predictions", heading_style))
            predictions = analysis_data['life_predictions']
            
            for key, value in predictions.items():
                title = key.replace('_', ' ').title()
                content.append(Paragraph(title, subheading_style))
                content.append(Paragraph(str(value), body_style))
            
            content.append(Spacer(1, 20))
        
        # Recommendations
        if 'recommendations' in analysis_data:
            content.append(Paragraph("Personal Recommendations", heading_style))
            recommendations = analysis_data['recommendations']
            
            for key, value in recommendations.items():
                title = key.replace('_', ' ').title()
                content.append(Paragraph(title, subheading_style))
                content.append(Paragraph(str(value), body_style))
            
            content.append(Spacer(1, 20))
        
        # Accuracy Note
        if 'accuracy_note' in analysis_data:
            content.append(Paragraph("About This Analysis", heading_style))
            content.append(Paragraph(analysis_data['accuracy_note'], body_style))
        
        # Disclaimer
        content.append(Spacer(1, 30))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=HexColor('#7f8c8d'),
            alignment=1
        )
        
        disclaimer_text = """
        DISCLAIMER: This analysis is for entertainment and self-reflection purposes only. 
        It should not be used as a substitute for professional medical, legal, or psychological advice. 
        The accuracy of ancient face reading systems is based on traditional beliefs and should be 
        interpreted as guidance rather than absolute truth. Please consult qualified professionals 
        for serious life decisions.
        """
        
        content.append(Paragraph(disclaimer_text, disclaimer_style))
        
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
