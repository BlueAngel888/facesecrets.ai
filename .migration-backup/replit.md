# Ancient Wisdom Face Analysis

## Overview

This is a Flask-based web application that provides AI-powered face analysis using ancient wisdom systems including Chinese Mian Xiang, Greek Physiognomy, Vedic Samudrika Shastra, Islamic Firasa, and modern FACS/Ekman techniques. The application uses OpenAI through Replit AI Integrations to analyze uploaded face images and generates comprehensive PDF reports in multiple languages.

## System Architecture

### Frontend Architecture
- **Framework**: React built with Vite and served by Flask from compiled static assets
- **UI Components**: 
  - Single-page responsive design with hero section
  - Multi-language support via dropdown selector
  - Drag-and-drop file upload interface
  - Camera capture functionality for mobile devices
  - Accessible React dialog and staged progress states
- **Styling**: Responsive custom CSS token system with reduced-motion support
- **Interaction**: React, Framer Motion, and Lucide icons

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Modular service-oriented architecture
  - `app.py`: Main Flask application with route handlers
  - `openai_service.py`: Replit-managed OpenAI vision integration
  - `pdf_service.py`: PDF generation using ReportLab
  - `translations.py`: Multi-language support system
- **Session Management**: Flask sessions for temporary data storage
- **File Handling**: Temporary file uploads with automatic cleanup

### Payment Integration
- **Stripe**: Credit card processing with hosted checkout
- **Flow**: Upload → Payment → Analysis → PDF Download
- **Security**: Payment handled entirely by Stripe's secure infrastructure

## Key Components

### Image Processing
- **Face Detection**: OpenCV for basic face validation
- **Image Handling**: PIL (Pillow) for image processing and validation
- **Upload Validation**: File type and size restrictions (16MB max, PNG/JPG/JPEG/GIF)

### AI Analysis Engine
- **OpenAI via Replit AI Integrations**: Managed multimodal analysis without a user-supplied API key
- **Analysis Framework**: 
  - Advanced Physiognomy & Morphopsychology (scientific approach)
  - Chinese Mian Xiang (secular 5-element system, 12-palace mapping)
  - Psychological Profiling (Big Five traits, cognitive styles)
  - Life Path & Potential Assessment (career aptitudes, leadership styles)
- **Comprehensive Reports**: 9-section detailed analysis including:
  - Executive Summary & Core Personality
  - Life Path Analysis (early/middle/wisdom years)
  - Professional Guidance & Career Development
  - Relationship Insights & Social Dynamics
  - Health, Vitality & Wellness
  - Financial Patterns & Wealth Building
  - Personal Development & Growth Plan
  - Strategic Action Plan (immediate/medium/long-term)
  - Advanced Insights & Hidden Potentials
- **Multi-language Output**: GPT-4o generates analysis in user's selected language
- **No Religious Content**: Secular approach focused on personal development

### PDF Report Generation
- **ReportLab**: Professional PDF generation with custom styling
- **Content Structure**: Multi-section comprehensive reports
- **Branding**: Custom colors and typography matching web design

### Internationalization
- **Languages Supported**: English, Romanian, German, Italian, French, Spanish, Chinese, Arabic, Japanese
- **Implementation**: Dictionary-based translations with language detection
- **Scope**: Full UI translation including PDF reports

## Data Flow

1. **User Journey**:
   - User selects language and uploads photo
   - Basic face detection validates image
   - Stripe payment processing
   - AI analysis via Replit-managed OpenAI
   - PDF report generation
   - Secure download and cleanup

2. **Data Processing**:
   - Image temporarily stored in `/static/uploads/`
   - Replit-managed OpenAI receives the base64-encoded image
   - Analysis results formatted into structured data
   - PDF generated in temporary location
   - All files automatically deleted post-download

3. **Security Flow**:
   - No persistent data storage
   - Automatic file cleanup after session
   - Session-based state management
   - GDPR-compliant privacy-by-design

## External Dependencies

### Core Services
- **Replit AI Integrations**: OpenAI multimodal model for face analysis
- **Stripe**: Payment processing (€29.99 per analysis)

### Python Libraries
- **Flask**: Web framework and routing
- **OpenCV**: Computer vision for face detection
- **PIL/Pillow**: Image processing
- **ReportLab**: PDF generation
- **Stripe**: Payment integration
- **NumPy**: Image array processing

### Frontend Dependencies
- **React**: Component-based user interface
- **Vite**: Reproducible frontend build
- **Framer Motion**: Accessible motion and transitions
- **Lucide React**: Interface icons

### Infrastructure
- **Replit**: Hosting platform with environment variable management
- **ProxyFix**: WSGI middleware for proper header handling

## Deployment Strategy

### Environment Configuration
- **Development**: Local Flask development server
- **Production**: Replit hosting with environment variables
- **Environment Variables**:
  - `AI_INTEGRATIONS_OPENAI_API_KEY`: Automatically provisioned Replit-managed credential
  - `AI_INTEGRATIONS_OPENAI_BASE_URL`: Automatically provisioned Replit-managed endpoint
  - `STRIPE_SECRET_KEY`: Stripe payment processing
  - `SESSION_SECRET`: Flask session encryption
  - `REPLIT_DEV_DOMAIN`: Dynamic domain handling

### File Management
- **Upload Directory**: `/static/uploads/` with automatic creation
- **Cleanup Strategy**: Automatic deletion after download/session end
- **Security**: Secure filename handling and file type validation

### Scalability Considerations
- **Stateless Design**: No database dependencies, session-based state
- **Memory Management**: Temporary file cleanup prevents storage accumulation
- **API Rate Limits**: OpenAI API usage monitoring needed for high volume

## Changelog

```
Changelog:
- July 06, 2025. Initial setup
- July 06, 2025. Added promo code functionality with "letsgo" for free analysis
- July 06, 2025. Configured custom domain support (facesecrets.ai)
- July 06, 2025. Major upgrade: Implemented GPT-4o comprehensive analysis with 9-section life path reports, advanced physiognomy, psychological profiling, and personal development action plans (non-religious approach)
- July 06, 2025. Extended advanced morphopsychology analysis to ALL supported languages (English, Romanian, German, Italian, French, Spanish, Chinese, Arabic, Japanese) with language-specific prompts and comprehensive error handling
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```