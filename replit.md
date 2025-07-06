# Ancient Wisdom Face Analysis

## Overview

This is a Flask-based web application that provides AI-powered face analysis using ancient wisdom systems including Chinese Mian Xiang, Greek Physiognomy, Vedic Samudrika Shastra, Islamic Firasa, and modern FACS/Ekman techniques. The application uses OpenAI's GPT-4 Vision API to analyze uploaded face images and generates comprehensive PDF reports in multiple languages.

## System Architecture

### Frontend Architecture
- **Framework**: Traditional server-side rendered Flask templates with Bootstrap 5
- **UI Components**: 
  - Single-page responsive design with hero section
  - Multi-language support via dropdown selector
  - Drag-and-drop file upload interface
  - Camera capture functionality for mobile devices
  - Modal-based loading states and interactions
- **Styling**: Custom CSS with CSS variables for theming, Bootstrap for responsive grid
- **JavaScript**: Vanilla JavaScript for file handling, camera integration, and payment flow

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Modular service-oriented architecture
  - `app.py`: Main Flask application with route handlers
  - `openai_service.py`: OpenAI GPT-4 Vision API integration
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
- **OpenAI GPT-4 Vision**: Core analysis engine using structured prompts
- **Analysis Systems**: 
  - Chinese Mian Xiang (100-year face mapping)
  - Greek Physiognomy (Aristotelian character analysis)
  - Vedic Samudrika Shastra (karmic indicators)
  - Islamic Firasa (spiritual essence reading)
  - Modern FACS/Ekman (micro-expression analysis)
- **Multi-language Output**: GPT-4 generates analysis in user's selected language

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
   - AI analysis via OpenAI GPT-4 Vision
   - PDF report generation
   - Secure download and cleanup

2. **Data Processing**:
   - Image temporarily stored in `/static/uploads/`
   - OpenAI API receives base64-encoded image
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
- **OpenAI API**: GPT-4 Vision for face analysis
- **Stripe**: Payment processing (€29.99 per analysis)

### Python Libraries
- **Flask**: Web framework and routing
- **OpenCV**: Computer vision for face detection
- **PIL/Pillow**: Image processing
- **ReportLab**: PDF generation
- **Stripe**: Payment integration
- **NumPy**: Image array processing

### Frontend Dependencies
- **Bootstrap 5**: CSS framework and components
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: No additional frameworks

### Infrastructure
- **Replit**: Hosting platform with environment variable management
- **ProxyFix**: WSGI middleware for proper header handling

## Deployment Strategy

### Environment Configuration
- **Development**: Local Flask development server
- **Production**: Replit hosting with environment variables
- **Environment Variables**:
  - `OPENAI_API_KEY`: OpenAI service authentication
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
- July 06, 2025. Configured custom domain support (facesecrets.com)
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```