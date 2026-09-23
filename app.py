import os
import logging
import json
import base64
from flask import Flask, render_template, request, jsonify, send_file, redirect, session, url_for
from werkzeug.exceptions import RequestEntityTooLarge
import stripe
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid
import tempfile
from PIL import Image
import cv2
import numpy as np
from openai_service import analyze_face_with_ai, translate_text
from pdf_service import generate_analysis_pdf
from translations import get_translations, SUPPORTED_LANGUAGES

# Configure logging
logging.basicConfig(level=logging.INFO)

SESSION_SECRET = os.environ.get("SESSION_SECRET")
if not SESSION_SECRET:
    raise RuntimeError(
        "SESSION_SECRET must be set to a strong, private value before starting the application."
    )

app = Flask(__name__)
app.secret_key = SESSION_SECRET
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Stripe configuration
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
# Domain configuration - supports custom domain via environment variable
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    YOUR_DOMAIN = CUSTOM_DOMAIN
elif os.environ.get('REPLIT_DEPLOYMENT'):
    YOUR_DOMAIN = os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]
else:
    YOUR_DOMAIN = 'localhost:5000'

# File upload configuration
UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'face-analysis-uploads')
REPORT_FOLDER = os.path.join(tempfile.gettempdir(), 'face-analysis-reports')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORT_FOLDER, exist_ok=True)

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=bool(os.environ.get('REPLIT_DEPLOYMENT')),
)

def safe_remove(path):
    if path:
        try:
            os.remove(path)
        except FileNotFoundError:
            pass
        except OSError as exc:
            logging.warning("Unable to remove temporary file: %s", exc)

def uploaded_path(filename):
    if not filename or filename != os.path.basename(filename):
        return None
    path = os.path.abspath(os.path.join(UPLOAD_FOLDER, filename))
    return path if os.path.dirname(path) == os.path.abspath(UPLOAD_FOLDER) else None

def report_path(report_id):
    if not report_id or report_id != os.path.basename(report_id):
        return None
    path = os.path.abspath(os.path.join(REPORT_FOLDER, report_id))
    return path if os.path.dirname(path) == os.path.abspath(REPORT_FOLDER) else None

def analysis_path(report_id):
    path = report_path(report_id)
    return f"{path}.json" if path else None

def load_analysis(report_id):
    path = analysis_path(report_id)
    if not path or not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as analysis_file:
        return json.load(analysis_file)

def clear_previous_upload():
    safe_remove(uploaded_path(session.get('uploaded_file')))
    session.pop('uploaded_file', None)

def run_analysis(filename, language):
    filepath = uploaded_path(filename)
    if not filepath or not os.path.exists(filepath):
        raise ValueError('Uploaded photo is no longer available. Please upload it again.')
    try:
        face_data = detect_face_landmarks(filepath)
        if not face_data:
            raise ValueError('No clear frontal face was detected. Use a well-lit, front-facing photo with one unobstructed face.')
        result = analyze_face_with_ai(filepath, language, face_data)
        if 'error' in result:
            raise RuntimeError(result.get('message', 'The analysis service is temporarily unavailable.'))
        report_id = f"analysis_{uuid.uuid4().hex}.pdf"
        path = report_path(report_id)
        generate_analysis_pdf(result, path, language)
        with open(analysis_path(report_id), 'w', encoding='utf-8') as analysis_file:
            json.dump(result, analysis_file, ensure_ascii=False)
        session['report_id'] = report_id
        session['analysis_complete'] = True
        return result
    finally:
        safe_remove(filepath)
        session.pop('uploaded_file', None)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_face_landmarks(image_path):
    """Simple face detection using OpenCV"""
    try:
        # Load the image
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Convert to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Load face cascade
        try:
            if hasattr(cv2, 'data') and hasattr(cv2.data, 'haarcascades'):
                cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            else:
                cascade_path = '/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception:
            # Alternative approach if cv2.data is not available
            face_cascade = cv2.CascadeClassifier('/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml')
        
        # Convert to grayscale for detection
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return None
        
        # Get the largest face
        largest_face = max(faces, key=lambda x: x[2] * x[3])
        x, y, w, h = largest_face
        
        # Extract basic features
        face_data = {
            'face_detected': True,
            'face_width': int(w),
            'face_height': int(h),
            'face_ratio': float(w/h),
            'face_area_percentage': float((w*h) / (image.shape[0] * image.shape[1]) * 100)
        }
        
        return face_data
    except Exception as e:
        logging.error(f"Face detection error: {e}")
        return None

@app.route('/')
def index():
    language = request.args.get('lang', 'en')
    if language not in SUPPORTED_LANGUAGES:
        language = 'en'
    
    translations = get_translations(language)
    return render_template('index.html', translations=translations, language=language, languages=SUPPORTED_LANGUAGES)

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        language = request.form.get('language', 'en')
        if language not in SUPPORTED_LANGUAGES:
            language = 'en'
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            clear_previous_upload()
            # Generate unique filename
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save file
            file.save(filepath)
            
            # Verify it's a valid image
            try:
                with Image.open(filepath) as img:
                    img.verify()
                with Image.open(filepath) as img:
                    if img.width < 256 or img.height < 256:
                        raise ValueError("Image is too small")
                    if img.width * img.height > 40_000_000:
                        raise ValueError("Image dimensions are too large")
                    img = img.convert('RGB')
                    img.thumbnail((2400, 2400))
                    filename = f"{uuid.uuid4().hex}.jpg"
                    normalized_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    img.save(normalized_path, 'JPEG', quality=92, optimize=True)
                safe_remove(filepath)
                filepath = normalized_path
            except Exception as e:
                os.remove(filepath)
                return jsonify({'error': 'Invalid image file'}), 400
            
            # Store file info in session for payment
            session['uploaded_file'] = filename
            session['language'] = language
            
            return jsonify({
                'success': True, 
                'filename': filename,
                'message': 'Image uploaded successfully. Proceed to payment to analyze.'
            })
        
        return jsonify({'error': 'Invalid file type'}), 400
    
    except Exception as e:
        logging.error(f"Upload error: {e}")
        return jsonify({'error': 'Upload failed'}), 500

@app.errorhandler(RequestEntityTooLarge)
def handle_oversized_upload(_error):
    return jsonify({'error': 'Image must be smaller than 16 MB'}), 413

@app.route('/check-promo-code', methods=['POST'])
def check_promo_code():
    try:
        data = request.get_json()
        promo_code = data.get('promo_code', '').strip().lower()
        
        if promo_code == 'letsgo':
            # Mark session as having valid free code
            session['free_analysis'] = True
            return jsonify({
                'success': True,
                'message': 'Promo code accepted! Free analysis unlocked.',
                'free_analysis': True
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid promo code. Please try again or proceed with payment.',
                'free_analysis': False
            })
    
    except Exception as e:
        logging.error(f"Promo code error: {e}")
        return jsonify({'error': 'Failed to check promo code'}), 500

@app.route('/free-analysis', methods=['POST'])
def free_analysis():
    try:
        if 'uploaded_file' not in session:
            return jsonify({'error': 'No file uploaded'}), 400
        
        if not session.get('free_analysis'):
            return jsonify({'error': 'Free analysis not authorized'}), 400
        
        uploaded_file = session.get('uploaded_file')
        language = session.get('language', 'en')
        
        if not uploaded_file:
            return jsonify({'error': 'No file found'}), 400
        
        analysis_result = run_analysis(uploaded_file, language)
        session['show_download'] = True
        session['free_analysis'] = False
        
        return jsonify({
            'success': True,
            'message': 'Free analysis complete! Your report is ready.',
            'redirect_url': '/success'
        })
    
    except Exception as e:
        logging.error(f"Free analysis error: {e}")
        return jsonify({'error': str(e) or 'Analysis failed'}), 500

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        if 'uploaded_file' not in session:
            return jsonify({'error': 'No file uploaded'}), 400
        
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'eur',
                        'product_data': {
                            'name': 'AI Face Analysis Report',
                            'description': 'Complete analysis using ancient wisdom and modern AI',
                        },
                        'unit_amount': 2999,  # 29.99 EUR in cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=f'https://{YOUR_DOMAIN}/success?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'https://{YOUR_DOMAIN}/cancel',
            automatic_tax={'enabled': False},
        )
        
        # Store session ID for verification
        session['stripe_session_id'] = checkout_session.id
        
        if checkout_session.url:
            return redirect(checkout_session.url, code=303)
        else:
            return jsonify({'error': 'Payment setup failed - no checkout URL'}), 500
    
    except Exception as e:
        logging.error(f"Stripe error: {e}")
        return jsonify({'error': 'Payment setup failed'}), 500

@app.route('/success')
def success():
    language = session.get('language', 'en')
    translations = get_translations(language)
    
    # Check for free analysis completion
    if session.get('show_download') and session.get('report_id'):
        analysis_result = load_analysis(session.get('report_id'))
        if not analysis_result:
            return redirect(url_for('index'))
        return render_template('success.html', 
                             analysis=analysis_result, 
                             pdf_ready=True,
                             free_analysis=True,
                             translations=translations,
                             language=language)
    
    # Handle Stripe payment success
    session_id = request.args.get('session_id')
    if not session_id or session_id != session.get('stripe_session_id'):
        return redirect(url_for('index'))
    
    try:
        # Verify payment with Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        if checkout_session.payment_status != 'paid':
            return redirect(url_for('cancel'))
        
        if session.get('analysis_complete') and session.get('report_id'):
            cached_result = load_analysis(session.get('report_id'))
            if cached_result:
                return render_template('success.html', analysis=cached_result,
                                   pdf_ready=True, translations=translations, language=language)

        uploaded_file = session.get('uploaded_file')
        if not uploaded_file:
            return redirect(url_for('index'))
        
        analysis_result = run_analysis(uploaded_file, language)
        
        translations = get_translations(language)
        return render_template('success.html', 
                             analysis=analysis_result, 
                             pdf_ready=True,
                             translations=translations,
                             language=language)
    
    except Exception as e:
        logging.error(f"Analysis error: {e}")
        translations = get_translations(language)
        return render_template('success.html', 
                             error=str(e),
                             translations=translations,
                             language=language)

@app.route('/download-pdf', methods=['GET'])
def download_pdf():
    pdf_path = report_path(session.get('report_id'))
    if not pdf_path:
        return jsonify({'error': 'No PDF file available'}), 404
    if not os.path.exists(pdf_path):
        return jsonify({'error': 'PDF file not found'}), 404
    try:
        with open(pdf_path, 'rb') as report:
            payload = report.read()
        safe_remove(pdf_path)
        safe_remove(analysis_path(session.get('report_id')))
        session.clear()
        return send_file(
            __import__('io').BytesIO(payload), as_attachment=True,
            download_name="face_analysis_report.pdf", mimetype='application/pdf'
        )
    except Exception as e:
        logging.error(f"Download error: {e}")
        return redirect(url_for('index'))

@app.route('/cancel')
def cancel():
    language = session.get('language', 'en')
    
    # Clean up any uploaded files
    uploaded_file = session.get('uploaded_file')
    if uploaded_file:
        safe_remove(uploaded_path(uploaded_file))
    
    # Clear session
    session.clear()
    
    translations = get_translations(language)
    return render_template('cancel.html', translations=translations, language=language)

@app.route('/translate', methods=['POST'])
def translate():
    try:
        data = request.get_json()
        text = data.get('text', '')
        target_language = data.get('language', 'en')
        
        translated_text = translate_text(text, target_language)
        return jsonify({'translated_text': translated_text})
    
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return jsonify({'error': 'Translation failed'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
