import os
import logging
import json
import base64
import hmac
import time
import hashlib
import secrets
import re
import subprocess
from collections import defaultdict, deque
from threading import Lock
from flask import Flask, render_template, request, jsonify, send_file, redirect, session, url_for
from werkzeug.exceptions import RequestEntityTooLarge
import stripe
import psycopg2
from psycopg2.extras import DictCursor
from werkzeug.utils import secure_filename
from werkzeug.middleware.proxy_fix import ProxyFix
import uuid
import tempfile
from pathlib import Path
from urllib.parse import quote, urlsplit
import urllib.error
import urllib.request
from PIL import Image
import cv2
import numpy as np
import file_store
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
def is_production():
    # A published Replit deployment or Vercel's production target.
    return bool(os.environ.get('REPLIT_DEPLOYMENT')) or os.environ.get('VERCEL_ENV') == 'production'

# Domain configuration - supports custom domain via environment variable
CUSTOM_DOMAIN = os.environ.get('CUSTOM_DOMAIN')
if CUSTOM_DOMAIN:
    YOUR_DOMAIN = CUSTOM_DOMAIN
elif os.environ.get('REPLIT_DEPLOYMENT'):
    YOUR_DOMAIN = os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]
elif os.environ.get('VERCEL'):
    YOUR_DOMAIN = (
        os.environ.get('VERCEL_PROJECT_PRODUCTION_URL') if is_production() else os.environ.get('VERCEL_URL')
    ) or 'localhost:5000'
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

REACT_BUILD = Path(app.static_folder) / 'react'

PROMO_CODE = os.environ.get('PROMO_CODE', '').strip()
AI_AUTHORIZATION_TTL_SECONDS = 60 * 60
MOBILE_TOKEN_TTL_SECONDS = 24 * 60 * 60
MOBILE_ANALYSIS_LEASE_SECONDS = 30 * 60
MAX_TRANSLATION_CHARACTERS = 4000
_rate_limit_events = defaultdict(deque)
_rate_limit_lock = Lock()

def page_payload(page='home', **page_data):
    return jsonify({'page': page, **page_data})

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=bool(os.environ.get('REPLIT_DEPLOYMENT') or os.environ.get('VERCEL')),
)

def request_source_is_same_origin():
    source = request.headers.get('Origin') or request.headers.get('Referer')
    if not source:
        return False

    source_url = urlsplit(source)
    expected_url = urlsplit(request.host_url)
    return (
        source_url.scheme.lower(),
        source_url.netloc.lower(),
    ) == (
        expected_url.scheme.lower(),
        expected_url.netloc.lower(),
    )

def configured_expo_origin():
    configured_domain = os.environ.get('REPLIT_EXPO_DEV_DOMAIN', '').strip()
    if not configured_domain:
        return None
    try:
        if '://' in configured_domain:
            parsed = urlsplit(configured_domain)
            if parsed.scheme.lower() != 'https':
                return None
        else:
            if any(char in configured_domain for char in '/?#'):
                return None
            parsed = urlsplit(f'https://{configured_domain}')
        if (
            not parsed.netloc
            or not parsed.hostname
            or parsed.username
            or parsed.password
            or parsed.path not in ('', '/')
            or parsed.query
            or parsed.fragment
        ):
            return None
        parsed.port
    except ValueError:
        return None
    return f'https://{parsed.netloc.lower()}'

def is_allowed_expo_origin(origin):
    allowed_origin = configured_expo_origin()
    if not allowed_origin or not origin:
        return False
    try:
        parsed = urlsplit(origin)
        return (
            parsed.scheme.lower() == 'https'
            and parsed.netloc.lower() == allowed_origin[len('https://'):]
            and parsed.hostname is not None
            and not parsed.username
            and not parsed.password
            and parsed.path == ''
            and not parsed.query
            and not parsed.fragment
        )
    except ValueError:
        return False

def is_expo_cors_resource():
    return request.path.startswith('/api/mobile/') or request.path == '/api/page'

def apply_expo_cors_headers(response, origin):
    response.headers['Access-Control-Allow-Origin'] = origin
    vary_values = response.headers.get('Vary', '').split(',')
    if 'origin' not in {value.strip().lower() for value in vary_values}:
        response.headers.add('Vary', 'Origin')
    return response

def safe_remove(path):
    if path:
        file_store.delete(path)
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

class MobileStorageUnavailable(RuntimeError):
    pass


class MobileConnection:
    """Small execute-compatible wrapper for mobile PostgreSQL transactions."""

    def __init__(self, connection):
        self.connection = connection
        self.cursors = []

    def execute(self, statement, parameters=()):
        cursor = self.connection.cursor(cursor_factory=DictCursor)
        self.cursors.append(cursor)
        cursor.execute(statement.replace('?', '%s'), parameters)
        return cursor

    def __enter__(self):
        return self

    def __exit__(self, exception_type, _exception, _traceback):
        try:
            if exception_type:
                self.connection.rollback()
            else:
                self.connection.commit()
        finally:
            for cursor in self.cursors:
                cursor.close()
            self.connection.close()


def mobile_db():
    database_url = (
        app.config.get('MOBILE_API_DATABASE_URL')
        or os.environ.get('DATABASE_URL')
    )
    if not database_url:
        raise MobileStorageUnavailable('DATABASE_URL is required for mobile storage')
    options = None
    schema = app.config.get('MOBILE_API_DATABASE_SCHEMA')
    if schema:
        if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', schema):
            raise MobileStorageUnavailable('Invalid mobile database schema name')
        options = f'-c search_path={schema}'
    connection = psycopg2.connect(database_url, connect_timeout=10, options=options)
    return MobileConnection(connection)

def remove_mobile_artifacts(row):
    if not row:
        return
    safe_remove(uploaded_path(row['uploaded_file']))
    if row['report_id']:
        safe_remove(report_path(row['report_id']))
        safe_remove(analysis_path(row['report_id']))

def cleanup_expired_mobile_sessions():
    now = int(time.time())
    with mobile_db() as connection:
        rows = connection.execute(
            'SELECT uploaded_file, report_id FROM mobile_sessions WHERE expires_at <= ?',
            (now,),
        ).fetchall()
        connection.execute('DELETE FROM mobile_sessions WHERE expires_at <= ?', (now,))
    for row in rows:
        remove_mobile_artifacts(row)

def mobile_token_hash(token):
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

REVENUECAT_API_BASE = 'https://api.revenuecat.com'

def revenuecat_api_purchases(project_id, app_user_id, product_id, secret_key):
    """Fetch the configured product's purchases from the RevenueCat v2 API.

    Mirrors scripts/src/revenueCatPurchases.ts for hosts without the Replit
    connector bridge (Vercel). Returns None on any failure.
    """
    project_path = f'/v2/projects/{quote(project_id, safe="")}'
    test_store_app_id = os.environ.get('REVENUECAT_TEST_STORE_APP_ID', '').strip()

    def get_page(path, customer_first_page):
        api_request = urllib.request.Request(
            f'{REVENUECAT_API_BASE}{path}',
            headers={'Authorization': f'Bearer {secret_key}', 'Accept': 'application/json'},
        )
        try:
            with urllib.request.urlopen(api_request, timeout=15) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as error:
            # RevenueCat does not create the customer until the SDK first sees them.
            if error.code == 404 and customer_first_page:
                return {'items': [], 'next_page': None}
            raise

    def list_all(initial_path, customer=False):
        path, visited, items = initial_path, set(), []
        while path:
            if not path.startswith(f'{project_path}/') or path in visited or len(visited) >= 1000:
                raise RuntimeError('Unexpected RevenueCat pagination')
            visited.add(path)
            page = get_page(path, customer and len(visited) == 1)
            if not isinstance(page.get('items'), list):
                raise RuntimeError('Unexpected RevenueCat response')
            items.extend(page['items'])
            path = page.get('next_page')
        return items

    try:
        catalog = list_all(f'{project_path}/products?limit=100')
        purchases = list_all(
            f'{project_path}/customers/{quote(app_user_id, safe="")}/purchases?limit=100', customer=True
        )
    except Exception:
        # Errors can include customer data; never log their details.
        return None
    products = {
        product['id']: product
        for product in catalog
        if isinstance(product, dict)
        and isinstance(product.get('id'), str)
        and (product.get('id') == product_id or product.get('store_identifier') == product_id)
        and (
            isinstance(product.get('app_id'), str) and product.get('app_id') != test_store_app_id
            if is_production() else product.get('app_id') == test_store_app_id
        )
    }
    return [
        {**purchase, 'revenuecat_product': products[purchase['product_id']]}
        for purchase in purchases
        if isinstance(purchase, dict) and purchase.get('product_id') in products
    ]

def revenuecat_customer_purchases(project_id, app_user_id):
    """Fetch RevenueCat purchases via the REST API when a secret key is set,
    otherwise through the Replit connector bridge."""
    secret_key = os.environ.get('REVENUECAT_SECRET_API_KEY', '').strip()
    if secret_key:
        return revenuecat_api_purchases(
            project_id, app_user_id, os.environ.get('REVENUECAT_PRODUCT_ID', '').strip(), secret_key
        )
    try:
        workspace_root = Path(__file__).resolve().parents[2]
        helper = workspace_root / 'scripts' / 'src' / 'revenueCatPurchases.ts'
        tsx = workspace_root / 'scripts' / 'node_modules' / '.bin' / 'tsx'
        completed = subprocess.run(
            [
                str(tsx),
                str(helper),
                project_id,
                app_user_id,
                os.environ.get('REVENUECAT_PRODUCT_ID', '').strip(),
            ],
            cwd=str(workspace_root),
            check=False,
            capture_output=True,
            text=True,
            timeout=45,
        )
        if completed.returncode != 0:
            return None
        payload = json.loads(completed.stdout)
        return payload if isinstance(payload, list) else None
    except Exception:
        # Bridge exceptions can include customer data or connector diagnostics.
        return None

def valid_revenuecat_purchase_transactions(
    purchases, configured_product_id, test_store_app_id, production=False
):
    transactions = []
    for purchase in purchases:
        if not isinstance(purchase, dict):
            continue
        product = purchase.get('revenuecat_product')
        if not isinstance(product, dict):
            continue
        if (
            product.get('id') != configured_product_id
            and product.get('store_identifier') != configured_product_id
        ):
            continue
        app_id = product.get('app_id')
        if not isinstance(app_id, str) or not app_id:
            continue
        if production and app_id == test_store_app_id:
            continue
        if not production and app_id != test_store_app_id:
            continue
        one_time = product.get('one_time')
        is_consumable = (
            product.get('type') == 'consumable'
            or (
                product.get('type') == 'one_time'
                and isinstance(one_time, dict)
                and one_time.get('is_consumable') is True
            )
        )
        if (
            not is_consumable
            or not isinstance(product.get('id'), str)
            or purchase.get('product_id') != product['id']
        ):
            continue
        # RevenueCat v2 purchase records expose owned/refunded and a store purchase identifier.
        if purchase.get('status') != 'owned':
            continue
        transaction_id = purchase.get('store_purchase_identifier')
        if isinstance(transaction_id, (str, int)) and str(transaction_id).strip():
            value = str(transaction_id).strip()
            if value not in transactions:
                transactions.append(value)
    return transactions

def authenticated_mobile_session():
    authorization = request.headers.get('Authorization', '')
    scheme, separator, token = authorization.partition(' ')
    if not separator or scheme.lower() != 'bearer' or not token or token.strip() != token:
        return None
    try:
        cleanup_expired_mobile_sessions()
        with mobile_db() as connection:
            return connection.execute(
                'SELECT * FROM mobile_sessions WHERE token_hash = ? AND expires_at > ?',
                (mobile_token_hash(token), int(time.time())),
            ).fetchone()
    except (psycopg2.Error, MobileStorageUnavailable):
        logging.exception('Unable to authenticate mobile API session')
        return None

def mobile_image_is_valid(path, original_filename):
    if not allowed_file(original_filename):
        return False
    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            if image.format not in {'JPEG', 'PNG', 'GIF'}:
                return False
            if image.width < 256 or image.height < 256:
                return False
            if image.width * image.height > 40_000_000:
                return False
            image = image.convert('RGB')
            image.thumbnail((2400, 2400))
            image.save(path + '.normalized.jpg', 'JPEG', quality=92, optimize=True)
        os.replace(path + '.normalized.jpg', path)
        return True
    except Exception:
        safe_remove(path)
        safe_remove(path + '.normalized.jpg')
        return False

def mobile_report_id_for(row):
    return row['report_id'] if row else None

def load_analysis(report_id):
    path = analysis_path(report_id)
    if not path or not file_store.fetch(path):
        return None
    with open(path, 'r', encoding='utf-8') as analysis_file:
        return json.load(analysis_file)

def clear_previous_upload():
    safe_remove(uploaded_path(session.get('uploaded_file')))
    session.pop('uploaded_file', None)

def run_analysis(filename, language):
    filepath = uploaded_path(filename)
    if not filepath or not file_store.fetch(filepath):
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
        file_store.save(path)
        file_store.save(analysis_path(report_id))
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

@app.route('/api/page')
def index():
    language = request.args.get('lang', 'en')
    if language not in SUPPORTED_LANGUAGES:
        language = 'en'
    
    return page_payload(
        language=language,
        languages=SUPPORTED_LANGUAGES,
        translations=get_translations(language),
    )

@app.route('/api/upload', methods=['POST'])
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
            
            file_store.save(filepath)
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

@app.route('/api/check-promo-code', methods=['POST'])
def check_promo_code():
    try:
        if ai_request_is_limited('promo-check', 10, 100, 10 * 60):
            return jsonify({'error': 'Too many promo code attempts. Please try again later.'}), 429
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid request'}), 400
        promo_code = data.get('promo_code', '').strip().lower()
        
        if PROMO_CODE and hmac.compare_digest(promo_code, PROMO_CODE.lower()):
            # This grant is short-lived and can fund at most one analysis.
            session['free_analysis'] = True
            session['free_analysis_expires_at'] = int(time.time()) + AI_AUTHORIZATION_TTL_SECONDS
            grant_ai_authorization()
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

@app.route('/api/free-analysis', methods=['POST'])
def free_analysis():
    try:
        if 'uploaded_file' not in session:
            return jsonify({'error': 'No file uploaded'}), 400
        
        if (
            not session.get('free_analysis')
            or session.get('free_analysis_expires_at', 0) < int(time.time())
        ):
            session.pop('free_analysis', None)
            session.pop('free_analysis_expires_at', None)
            return jsonify({'error': 'Free analysis not authorized'}), 403
        if ai_request_is_limited('free-analysis', 2, 30, 60 * 60):
            return jsonify({'error': 'Analysis limit reached. Please try again later.'}), 429
        
        uploaded_file = session.get('uploaded_file')
        language = session.get('language', 'en')
        
        if not uploaded_file:
            return jsonify({'error': 'No file found'}), 400
        
        # Consume the grant before starting the billable call so retries cannot reuse it.
        session.pop('free_analysis', None)
        session.pop('free_analysis_expires_at', None)
        analysis_result = run_analysis(uploaded_file, language)
        session['show_download'] = True
        
        return jsonify({
            'success': True,
            'message': 'Free analysis complete! Your report is ready.',
            'redirect_url': '/success'
        })
    
    except Exception as e:
        logging.error(f"Free analysis error: {e}")
        return jsonify({'error': str(e) or 'Analysis failed'}), 500

@app.route('/api/create-checkout-session', methods=['POST'])
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
        
        if checkout_session.url and request.accept_mimetypes.best == 'application/json':
            return jsonify({'checkout_url': checkout_session.url})
        if checkout_session.url:
            return redirect(checkout_session.url, code=303)
        else:
            return jsonify({'error': 'Payment setup failed - no checkout URL'}), 500
    
    except Exception as e:
        logging.error(f"Stripe error: {e}")
        return jsonify({'error': 'Payment setup failed'}), 500

@app.route('/api/success')
def success():
    language = session.get('language', 'en')
    translations = get_translations(language)
    
    # Check for free analysis completion
    if session.get('show_download') and session.get('report_id'):
        analysis_result = load_analysis(session.get('report_id'))
        if not analysis_result:
            return redirect(url_for('index'))
        return page_payload(page='success', analysis=analysis_result,
                            pdf_ready=True, free_analysis=True,
                            translations=translations, language=language)
    
    # Handle Stripe payment success
    session_id = request.args.get('session_id')
    if not session_id or session_id != session.get('stripe_session_id'):
        return redirect(url_for('index'))
    
    try:
        # Verify payment with Stripe
        checkout_session = stripe.checkout.Session.retrieve(session_id)
        
        if checkout_session.payment_status != 'paid':
            return redirect(url_for('cancel'))
        grant_ai_authorization()
        
        if session.get('analysis_complete') and session.get('report_id'):
            cached_result = load_analysis(session.get('report_id'))
            if cached_result:
                return page_payload(page='success', analysis=cached_result,
                                    pdf_ready=True, translations=translations, language=language)

        uploaded_file = session.get('uploaded_file')
        if not uploaded_file:
            return redirect(url_for('index'))
        
        analysis_result = run_analysis(uploaded_file, language)
        
        translations = get_translations(language)
        return page_payload(page='success', analysis=analysis_result,
                            pdf_ready=True, translations=translations, language=language)
    
    except Exception as e:
        logging.error(f"Analysis error: {e}")
        translations = get_translations(language)
        return page_payload(page='error', error=str(e),
                            translations=translations, language=language)

@app.route('/api/download-pdf', methods=['POST'])
def download_pdf():
    pdf_path = report_path(session.get('report_id'))
    if not pdf_path:
        return jsonify({'error': 'No PDF file available'}), 404
    if not file_store.fetch(pdf_path):
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

@app.route('/api/cancel', methods=['GET', 'POST'])
def cancel():
    language = session.get('language', 'en')

    if request.method == 'POST':
        safe_remove(uploaded_path(session.get('uploaded_file')))
        session.clear()
        return jsonify({'success': True, 'redirect_url': '/'})

    return page_payload(page='cancel', translations=get_translations(language), language=language)

@app.route('/api/translate', methods=['POST'])
def translate():
    try:
        if not has_ai_authorization():
            return jsonify({'error': 'Payment or a valid promotion is required'}), 403
        if ai_request_is_limited('translate', 20, 200, 60 * 60):
            return jsonify({'error': 'Translation limit reached. Please try again later.'}), 429
        data = request.get_json(silent=True)
        if not isinstance(data, dict):
            return jsonify({'error': 'Invalid request'}), 400
        text = data.get('text', '')
        target_language = data.get('language', 'en')
        if not isinstance(text, str) or not text.strip():
            return jsonify({'error': 'Text is required'}), 400
        if len(text) > MAX_TRANSLATION_CHARACTERS:
            return jsonify({
                'error': f'Text must be {MAX_TRANSLATION_CHARACTERS} characters or fewer'
            }), 413
        if target_language not in SUPPORTED_LANGUAGES:
            return jsonify({'error': 'Unsupported language'}), 400
        
        translated_text = translate_text(text, target_language)
        return jsonify({'translated_text': translated_text})
    
    except Exception as e:
        logging.error(f"Translation error: {e}")
        return jsonify({'error': 'Translation failed'}), 500

@app.route('/api/mobile/session', methods=['POST'])
def mobile_create_session():
    if ai_request_is_limited('mobile-session', 10, 100, 10 * 60):
        return jsonify({'error': 'Too many mobile sessions created. Please try again later.'}), 429
    request_data = request.get_json(silent=True)
    if request_data is None:
        request_data = {}
    if not isinstance(request_data, dict):
        return jsonify({'error': 'Invalid request'}), 400
    supplied_device_token = 'device_token' in request_data
    device_token = request_data.get('device_token')
    if supplied_device_token and (
        not isinstance(device_token, str)
        or not device_token
        or device_token.strip() != device_token
    ):
        return jsonify({'error': 'Valid device token required'}), 401

    try:
        cleanup_expired_mobile_sessions()
    except (psycopg2.Error, MobileStorageUnavailable):
        logging.exception('Unable to clean up expired mobile sessions')
        return jsonify({'error': 'Mobile session storage is unavailable'}), 503
    token = secrets.token_urlsafe(32)
    expires_at = int(time.time()) + MOBILE_TOKEN_TTL_SECONDS
    if not supplied_device_token:
        device_token = secrets.token_urlsafe(32)
        device_token_hash = mobile_token_hash(device_token)
        rc_app_user_id = str(uuid.uuid4())
    else:
        device_token_hash = mobile_token_hash(device_token)
    try:
        with mobile_db() as connection:
            if supplied_device_token:
                device = connection.execute(
                    '''SELECT rc_app_user_id FROM mobile_devices
                       WHERE device_token_hash = ?''',
                    (device_token_hash,),
                ).fetchone()
                if not device:
                    return jsonify({'error': 'Valid device token required'}), 401
                rc_app_user_id = device['rc_app_user_id']
            else:
                connection.execute(
                    '''INSERT INTO mobile_devices
                       (device_token_hash, rc_app_user_id, created_at)
                       VALUES (?, ?, ?)''',
                    (device_token_hash, rc_app_user_id, int(time.time())),
                )
            connection.execute(
                '''INSERT INTO mobile_sessions
                   (token_hash, expires_at, device_token_hash, rc_app_user_id)
                   VALUES (?, ?, ?, ?)''',
                (
                    mobile_token_hash(token), expires_at, device_token_hash,
                    rc_app_user_id,
                ),
            )
    except (psycopg2.Error, MobileStorageUnavailable):
        logging.exception('Unable to create mobile API session')
        return jsonify({'error': 'Unable to create session'}), 503
    response = jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_at': expires_at,
        'expires_in': MOBILE_TOKEN_TTL_SECONDS,
        'device_token': device_token,
        'rc_app_user_id': rc_app_user_id,
    })
    response.headers['Cache-Control'] = 'private, no-store'
    return response, 201

@app.route('/api/mobile/upload', methods=['POST'])
def mobile_upload():
    mobile_session = authenticated_mobile_session()
    if not mobile_session:
        return jsonify({'error': 'Valid bearer token required'}), 401
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    uploaded = request.files['file']
    if not uploaded.filename:
        return jsonify({'error': 'No file selected'}), 400
    language = request.form.get('language', '')
    if language not in SUPPORTED_LANGUAGES:
        return jsonify({'error': 'Unsupported language'}), 400
    if not allowed_file(uploaded.filename):
        return jsonify({'error': 'Invalid file type'}), 400

    filename = f"mobile_{uuid.uuid4().hex}.jpg"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    try:
        uploaded.save(filepath)
        if not mobile_image_is_valid(filepath, uploaded.filename):
            return jsonify({'error': 'Invalid image file or dimensions'}), 400
        file_store.save(filepath)
        with mobile_db() as connection:
            previous = connection.execute(
                'SELECT uploaded_file, report_id FROM mobile_sessions WHERE token_hash = ? AND expires_at > ?',
                (mobile_session['token_hash'], int(time.time())),
            ).fetchone()
            if not previous:
                safe_remove(filepath)
                return jsonify({'error': 'Mobile session has expired'}), 401
            updated = connection.execute(
                '''UPDATE mobile_sessions
                   SET uploaded_file = ?, language = ?, report_id = NULL, analysis_json = NULL
                   WHERE token_hash = ? AND expires_at > ?''',
                (filename, language, mobile_session['token_hash'], int(time.time())),
            ).rowcount
        if not updated:
            safe_remove(filepath)
            return jsonify({'error': 'Mobile session has expired'}), 401
        remove_mobile_artifacts(previous)
        return jsonify({
            'success': True,
            'message': 'Portrait uploaded successfully.',
        })
    except Exception:
        logging.exception('Mobile portrait upload failed')
        safe_remove(filepath)
        return jsonify({'error': 'Upload failed'}), 500
    finally:
        safe_remove(filepath + '.normalized.jpg')

@app.route('/api/mobile/promo', methods=['POST'])
def mobile_check_promo():
    mobile_session = authenticated_mobile_session()
    if not mobile_session:
        return jsonify({'error': 'Valid bearer token required'}), 401
    if ai_request_is_limited('mobile-promo', 10, 100, 10 * 60):
        return jsonify({'error': 'Too many promo code attempts. Please try again later.'}), 429
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not isinstance(data.get('promo_code'), str):
        return jsonify({'error': 'Invalid request'}), 400
    submitted_code = data['promo_code'].strip().lower()
    if not PROMO_CODE or not hmac.compare_digest(submitted_code, PROMO_CODE.lower()):
        return jsonify({
            'success': False,
            'message': 'Invalid promo code.',
            'free_analysis': False,
        })

    grant_expiry = int(time.time()) + AI_AUTHORIZATION_TTL_SECONDS
    with mobile_db() as connection:
        updated = connection.execute(
            '''UPDATE mobile_sessions
               SET grant_expires_at = ?, grant_issued = 1, grant_used = 0,
                   promo_issued = 1
               WHERE token_hash = ? AND expires_at > ? AND promo_issued = 0
                 AND grant_used <> 2
                 AND (
                     grant_issued = 0 OR grant_used = 1 OR grant_expires_at < ?
                 )''',
            (grant_expiry, mobile_session['token_hash'], int(time.time()), int(time.time())),
        ).rowcount
    if not updated:
        return jsonify({
            'success': False,
            'message': 'This mobile session has already used its promotion grant.',
            'free_analysis': False,
        }), 409
    return jsonify({
        'success': True,
        'message': 'Promo code accepted. One analysis is unlocked.',
        'free_analysis': True,
        'expires_at': grant_expiry,
    })

@app.route('/api/mobile/redeem', methods=['POST'])
def mobile_redeem_purchase():
    mobile_session = authenticated_mobile_session()
    if not mobile_session:
        return jsonify({'error': 'Valid bearer token required'}), 401
    if ai_request_is_limited('mobile-redeem', 10, 100, 10 * 60):
        return jsonify({'error': 'Too many redemption attempts. Please try again later.'}), 429

    project_id = os.environ.get('REVENUECAT_PROJECT_ID', '').strip()
    product_id = os.environ.get('REVENUECAT_PRODUCT_ID', '').strip()
    test_store_app_id = os.environ.get('REVENUECAT_TEST_STORE_APP_ID', '').strip()
    if (
        not project_id
        or not product_id
        or not test_store_app_id
        or not mobile_session['rc_app_user_id']
    ):
        return jsonify({'error': 'Purchase verification is not configured.'}), 503

    verified_purchases = revenuecat_customer_purchases(
        project_id, mobile_session['rc_app_user_id']
    )
    if verified_purchases is None:
        return jsonify({'error': 'Purchase verification is temporarily unavailable.'}), 503
    transactions = valid_revenuecat_purchase_transactions(
        verified_purchases,
        product_id,
        test_store_app_id,
        production=is_production(),
    )
    if not transactions:
        return jsonify({'error': 'No valid, non-refunded consumable purchase was found.'}), 402

    now = int(time.time())
    grant_expiry = now + AI_AUTHORIZATION_TTL_SECONDS
    try:
        with mobile_db() as connection:
            current = connection.execute(
                '''SELECT grant_issued, grant_used, grant_expires_at, expires_at
                   FROM mobile_sessions
                   WHERE token_hash = ? AND expires_at > ?
                   FOR UPDATE''',
                (mobile_session['token_hash'], now),
            ).fetchone()
            if not current:
                return jsonify({'error': 'Mobile session has expired.'}), 401
            if (
                current['grant_issued']
                and (
                    current['grant_used'] == 2
                    or (
                        not current['grant_used']
                        and current['grant_expires_at']
                        and current['grant_expires_at'] >= now
                    )
                )
            ):
                return jsonify({
                    'error': 'This mobile session already has an unused analysis grant.'
                }), 409
            transaction_id = None
            for candidate in transactions:
                inserted = connection.execute(
                    '''INSERT INTO mobile_purchase_redemptions
                       (transaction_id, token_hash, redeemed_at)
                       VALUES (?, ?, ?) ON CONFLICT (transaction_id) DO NOTHING
                       RETURNING transaction_id''',
                    (candidate, mobile_session['token_hash'], now),
                ).fetchone()
                if inserted:
                    transaction_id = candidate
                    break
            if not transaction_id:
                return jsonify({'error': 'No unredeemed consumable purchase was found.'}), 409
            grant_issued = connection.execute(
                '''UPDATE mobile_sessions
                   SET grant_expires_at = ?, grant_issued = 1, grant_used = 0
                   WHERE token_hash = ? AND expires_at > ?''',
                (grant_expiry, mobile_session['token_hash'], now),
            ).rowcount
            if grant_issued != 1:
                raise RuntimeError('Mobile grant could not be issued')
    except psycopg2.IntegrityError:
        return jsonify({'error': 'This purchase has already been redeemed.'}), 409
    except (psycopg2.Error, MobileStorageUnavailable):
        logging.error('Unable to persist mobile purchase redemption')
        return jsonify({'error': 'Purchase redemption storage is unavailable.'}), 503

    return jsonify({
        'success': True,
        'message': 'Purchase verified. One analysis is unlocked.',
        'free_analysis': True,
        'expires_at': grant_expiry,
    })

@app.route('/api/mobile/analyze', methods=['POST'])
def mobile_analyze():
    mobile_session = authenticated_mobile_session()
    if not mobile_session:
        return jsonify({'error': 'Valid bearer token required'}), 401
    if ai_request_is_limited('mobile-analysis', 2, 30, 60 * 60):
        return jsonify({'error': 'Analysis limit reached. Please try again later.'}), 429

    filepath = uploaded_path(mobile_session['uploaded_file'])
    if not filepath or not file_store.fetch(filepath):
        return jsonify({'error': 'Upload a valid portrait before analysis.'}), 400

    now = int(time.time())
    lease_expires_at = now + MOBILE_ANALYSIS_LEASE_SECONDS
    with mobile_db() as connection:
        claim = connection.execute(
            '''UPDATE mobile_sessions
               SET grant_used = 2, grant_expires_at = ?
               WHERE token_hash = ? AND expires_at > ? AND grant_issued = 1
                 AND (
                     (grant_used = 0 AND grant_expires_at >= ?)
                     OR (grant_used = 2 AND grant_expires_at < ?)
                 )
               RETURNING language''',
            (
                lease_expires_at, mobile_session['token_hash'], now, now, now,
            ),
        ).fetchone()
        if claim:
            language = claim['language'] or 'en'
        else:
            current = connection.execute(
                '''SELECT grant_issued, grant_used, grant_expires_at
                   FROM mobile_sessions WHERE token_hash = ? AND expires_at > ?''',
                (mobile_session['token_hash'], now),
            ).fetchone()
            if (
                current
                and current['grant_issued']
                and current['grant_used'] == 2
                and current['grant_expires_at']
                and current['grant_expires_at'] >= now
            ):
                return jsonify({'error': 'An analysis is already in progress.'}), 409
            return jsonify({'error': 'A valid, unused analysis grant is required.'}), 403

    created_report = None
    analysis_committed = False
    try:
        face_data = detect_face_landmarks(filepath)
        if not face_data:
            return jsonify({
                'error': 'No clear frontal face was detected. Use a well-lit, front-facing photo with one unobstructed face.'
            }), 422
        result = analyze_face_with_ai(filepath, language, face_data)
        if not isinstance(result, dict) or 'error' in result:
            message = result.get('message', 'The analysis service is temporarily unavailable.') if isinstance(result, dict) else 'The analysis service is temporarily unavailable.'
            return jsonify({'error': message}), 503
        created_report = f"mobile_analysis_{uuid.uuid4().hex}.pdf"
        generate_analysis_pdf(result, report_path(created_report), language)
        encoded_result = json.dumps(result, ensure_ascii=False)
        with mobile_db() as connection:
            updated = connection.execute(
                '''UPDATE mobile_sessions
                   SET report_id = ?, analysis_json = ?, uploaded_file = NULL, grant_used = 1
                   WHERE token_hash = ? AND expires_at > ?
                     AND grant_used = 2 AND grant_expires_at = ?''',
                (
                    created_report, encoded_result, mobile_session['token_hash'],
                    int(time.time()), lease_expires_at,
                ),
            ).rowcount
        if not updated:
            raise RuntimeError('Mobile analysis lease was lost before completion.')
        analysis_committed = True
        response = jsonify({
            'success': True,
            'analysis': result,
            'report_url': '/api/mobile/report',
        })
        response.headers['Cache-Control'] = 'private, no-store'
        return response
    except Exception:
        logging.exception('Mobile analysis failed')
        if created_report:
            safe_remove(report_path(created_report))
        return jsonify({'error': 'Analysis failed. Your grant is available to retry.'}), 500
    finally:
        if not analysis_committed:
            try:
                with mobile_db() as connection:
                    connection.execute(
                        '''UPDATE mobile_sessions
                           SET grant_used = 0, grant_expires_at = ?
                           WHERE token_hash = ? AND grant_used = 2
                             AND grant_expires_at = ?''',
                        (
                            int(time.time()) + AI_AUTHORIZATION_TTL_SECONDS,
                            mobile_session['token_hash'],
                            lease_expires_at,
                        ),
                    )
            except Exception:
                # A process or storage failure leaves the lease reclaimable after expiry.
                logging.error('Unable to release failed mobile analysis grant')
        safe_remove(filepath)

@app.route('/api/mobile/result', methods=['GET'])
def mobile_result():
    mobile_session = authenticated_mobile_session()
    if not mobile_session:
        return jsonify({'error': 'Valid bearer token required'}), 401
    if not mobile_session['analysis_json']:
        return jsonify({'error': 'No analysis is available'}), 404
    response = jsonify({
        'success': True,
        'analysis': json.loads(mobile_session['analysis_json']),
        'report_url': '/api/mobile/report',
    })
    response.headers['Cache-Control'] = 'private, no-store'
    return response

@app.route('/api/mobile/report', methods=['GET'])
def mobile_report():
    mobile_session = authenticated_mobile_session()
    if not mobile_session:
        return jsonify({'error': 'Valid bearer token required'}), 401
    filepath = report_path(mobile_report_id_for(mobile_session))
    if not filepath or not mobile_session['analysis_json']:
        return jsonify({'error': 'No PDF report is available'}), 404
    if not os.path.isfile(filepath):
        temporary_path = f'{filepath}.{uuid.uuid4().hex}.tmp'
        try:
            # Reports can be reconstructed from the persisted analysis after a
            # server restart; temp files are not durable across deployments.
            generate_analysis_pdf(
                json.loads(mobile_session['analysis_json']),
                temporary_path,
                mobile_session['language'] or 'en',
            )
            os.replace(temporary_path, filepath)
        except Exception:
            safe_remove(temporary_path)
            logging.exception('Unable to reconstruct mobile PDF report')
            return jsonify({'error': 'Report is temporarily unavailable'}), 503
    response = send_file(
        filepath, as_attachment=True, download_name='portrait_reflection_report.pdf',
        mimetype='application/pdf', max_age=0,
    )
    response.headers['Cache-Control'] = 'private, no-store'
    return response

@app.route('/api/mobile/cancel', methods=['POST'])
def mobile_cancel():
    mobile_session = authenticated_mobile_session()
    if not mobile_session:
        return jsonify({'error': 'Valid bearer token required'}), 401
    with mobile_db() as connection:
        connection.execute(
            'DELETE FROM mobile_sessions WHERE token_hash = ?',
            (mobile_session['token_hash'],),
        )
    remove_mobile_artifacts(mobile_session)
    return jsonify({'success': True})

def client_ip():
    return request.remote_addr or 'unknown'

def ai_request_is_limited(scope, ip_limit, global_limit, window_seconds):
    return (
        rate_limit_exceeded(scope, ip_limit, window_seconds, per_ip=True)
        or rate_limit_exceeded(scope, global_limit, window_seconds, per_ip=False)
    )

def grant_ai_authorization():
    session['ai_authorized_until'] = int(time.time()) + AI_AUTHORIZATION_TTL_SECONDS

def has_ai_authorization():
    return session.get('ai_authorized_until', 0) >= int(time.time())

def rate_limit_exceeded(scope, limit, window_seconds, per_ip=True):
    now = time.monotonic()
    key = (scope, client_ip() if per_ip else 'global')
    with _rate_limit_lock:
        events = _rate_limit_events[key]
        cutoff = now - window_seconds
        while events and events[0] <= cutoff:
            events.popleft()
        if len(events) >= limit:
            return True
        events.append(now)
        return False

@app.before_request
def reject_cross_site_state_changes():
    origin = request.headers.get('Origin')
    if request.method == 'OPTIONS' and is_expo_cors_resource() and origin:
        if not is_allowed_expo_origin(origin):
            return jsonify({'error': 'Origin is not allowed'}), 403
        requested_method = request.headers.get('Access-Control-Request-Method', '').upper()
        route_methods = set(request.url_rule.methods or ()) if request.url_rule else set()
        route_methods.discard('OPTIONS')
        route_methods.discard('HEAD')
        if requested_method not in route_methods:
            return jsonify({'error': 'Preflight method is not allowed'}), 403
        allowed_request_headers = {'authorization', 'content-type', 'accept'}
        requested_headers = {
            header.strip().lower()
            for header in request.headers.get('Access-Control-Request-Headers', '').split(',')
            if header.strip()
        }
        if not requested_headers.issubset(allowed_request_headers):
            return jsonify({'error': 'Preflight headers are not allowed'}), 403
        response = app.response_class(status=204)
        response.headers['Access-Control-Allow-Methods'] = requested_method
        if requested_headers:
            response.headers['Access-Control-Allow-Headers'] = ', '.join(
                header.title() for header in sorted(requested_headers)
            )
        response.headers['Access-Control-Max-Age'] = '600'
        return apply_expo_cors_headers(response, origin)
    if (
        request.path.startswith('/api/mobile/')
        and origin
        and is_allowed_expo_origin(origin)
    ):
        return None
    if (
        request.path.startswith('/api/mobile/')
        and not request.headers.get('Origin')
        and not request.headers.get('Referer')
    ):
        return None
    if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and not request_source_is_same_origin():
        return jsonify({'error': 'Cross-site request blocked'}), 403

@app.after_request
def add_expo_cors_headers(response):
    origin = request.headers.get('Origin')
    if (
        origin
        and is_allowed_expo_origin(origin)
        and is_expo_cors_resource()
        and (
            request.path.startswith('/api/mobile/')
            or request.method == 'GET'
        )
    ):
        apply_expo_cors_headers(response, origin)
    return response

@app.route('/api/healthz')
def healthz():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8080')))
