import io
import os
import subprocess
import sys
import tomllib
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

import app as face_app
import openai_service


def image_bytes(size=(640, 640)):
    buffer = io.BytesIO()
    Image.new('RGB', size, 'tan').save(buffer, 'JPEG')
    buffer.seek(0)
    return buffer


SAMPLE_RESULT = {
    'executive_summary': 'A clear frontal photograph with good lighting.',
    'image_quality': {'overall': 'good', 'confidence': 'high', 'limitations': []},
    'analiza_trasaturi': {'fruntea': 'Clearly visible.'},
    'traditional_perspectives': {'mian_xiang': 'A cultural reflection, not a fact.'},
    'profil_psihologic': 'Psychology cannot be determined from appearance.',
    'recomandari_dezvoltare': {'reflectie': 'Use open questions.'},
    'tips_long_term': ['Journal observations separately from interpretations.'],
    'disclaimer': 'Not a medical, psychological, or predictive assessment.',
}


class FlowTests(unittest.TestCase):
    def setUp(self):
        face_app.app.config.update(TESTING=True, SECRET_KEY='test')
        face_app._rate_limit_events.clear()
        self.client = face_app.app.test_client()
        self.client.environ_base['HTTP_ORIGIN'] = 'http://localhost'

    def upload(self, size=(640, 640)):
        return self.client.post('/upload', data={
            'file': (image_bytes(size), 'face.jpg'),
            'language': 'en',
        }, content_type='multipart/form-data')

    def test_rejects_invalid_and_small_images(self):
        response = self.client.post('/upload', data={
            'file': (io.BytesIO(b'not an image'), 'bad.jpg'),
            'language': 'en',
        }, content_type='multipart/form-data')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(self.upload((100, 100)).status_code, 400)

    @patch.object(face_app, 'detect_face_landmarks', return_value={'face_detected': True})
    @patch.object(face_app, 'analyze_face_with_ai', return_value=SAMPLE_RESULT)
    def test_complete_free_flow_and_single_use_private_download(self, _ai, _detect):
        self.assertEqual(self.upload().status_code, 200)
        with self.client.session_transaction() as session:
            session['free_analysis'] = True
            session['free_analysis_expires_at'] = int(face_app.time.time()) + 60
        analyzed = self.client.post('/free-analysis')
        self.assertEqual(analyzed.status_code, 200)
        self.assertNotIn('pdf_path', analyzed.get_json())
        results = self.client.get('/success')
        self.assertEqual(results.status_code, 200)
        self.assertIn(b'executive_summary', results.data)
        self.assertIn(SAMPLE_RESULT['executive_summary'].encode(), results.data)
        download = self.client.post('/download-pdf')
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.mimetype, 'application/pdf')
        self.assertTrue(download.data.startswith(b'%PDF'))
        self.assertEqual(self.client.post('/download-pdf').status_code, 404)

    @patch.object(face_app.stripe.checkout.Session, 'retrieve')
    @patch.object(face_app, 'detect_face_landmarks', return_value={'face_detected': True})
    @patch.object(face_app, 'analyze_face_with_ai', return_value=SAMPLE_RESULT)
    def test_paid_success_is_idempotent(self, ai_mock, _detect, retrieve_mock):
        self.assertEqual(self.upload().status_code, 200)
        retrieve_mock.return_value.payment_status = 'paid'
        with self.client.session_transaction() as session:
            session['stripe_session_id'] = 'checkout_123'
        first = self.client.get('/success?session_id=checkout_123')
        second = self.client.get('/success?session_id=checkout_123')
        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(ai_mock.call_count, 1)
        self.assertEqual(retrieve_mock.call_count, 2)
        retrieve_mock.assert_called_with('checkout_123')

    def test_download_does_not_accept_paths(self):
        response = self.client.post('/download-pdf', json={'pdf_path': '/etc/passwd'})
        self.assertEqual(response.status_code, 404)

    def test_session_cookie_uses_lax_samesite(self):
        self.assertEqual(face_app.app.config['SESSION_COOKIE_SAMESITE'], 'Lax')

    def test_cross_site_upload_is_rejected_without_replacing_session_photo(self):
        with self.client.session_transaction() as session:
            session['uploaded_file'] = 'existing.jpg'
        response = self.client.post('/upload', data={
            'file': (image_bytes(), 'attacker.jpg'),
            'language': 'en',
        }, content_type='multipart/form-data', headers={
            'Origin': 'https://attacker-controlled.example',
        })
        self.assertEqual(response.status_code, 403)
        with self.client.session_transaction() as session:
            self.assertEqual(session['uploaded_file'], 'existing.jpg')

    @patch.object(face_app.stripe.checkout.Session, 'create')
    def test_cross_site_checkout_is_rejected_before_stripe_call(self, create_mock):
        with self.client.session_transaction() as session:
            session['uploaded_file'] = 'existing.jpg'
        response = self.client.post('/create-checkout-session', headers={
            'Origin': 'https://attacker-controlled.example',
        })
        self.assertEqual(response.status_code, 403)
        create_mock.assert_not_called()

    @patch.object(face_app, 'run_analysis')
    def test_cross_site_free_analysis_is_rejected_without_consuming_promo(self, analysis_mock):
        with self.client.session_transaction() as session:
            session['uploaded_file'] = 'existing.jpg'
            session['free_analysis'] = True
            session['free_analysis_expires_at'] = int(face_app.time.time()) + 60
        response = self.client.post('/free-analysis', headers={
            'Origin': 'https://attacker-controlled.example',
        })
        self.assertEqual(response.status_code, 403)
        analysis_mock.assert_not_called()
        with self.client.session_transaction() as session:
            self.assertTrue(session['free_analysis'])

    def test_same_origin_referer_is_accepted(self):
        client = face_app.app.test_client()
        response = client.post('/check-promo-code', json={
            'promo_code': 'letsgo',
        }, headers={'Referer': 'http://localhost/'})
        self.assertEqual(response.status_code, 200)

    def test_get_cannot_consume_report(self):
        with self.client.session_transaction() as session:
            session['report_id'] = 'existing.pdf'
        response = self.client.get('/download-pdf')
        self.assertEqual(response.status_code, 405)
        with self.client.session_transaction() as session:
            self.assertEqual(session['report_id'], 'existing.pdf')

    def test_get_cancel_does_not_clear_session(self):
        with self.client.session_transaction() as session:
            session['uploaded_file'] = 'existing.jpg'
        response = self.client.get('/cancel')
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as session:
            self.assertEqual(session['uploaded_file'], 'existing.jpg')

    def test_cross_site_cancel_post_is_rejected_without_clearing_session(self):
        with self.client.session_transaction() as session:
            session['uploaded_file'] = 'existing.jpg'
        response = self.client.post('/cancel', headers={
            'Origin': 'https://attacker-controlled.example',
        })
        self.assertEqual(response.status_code, 403)
        with self.client.session_transaction() as session:
            self.assertEqual(session['uploaded_file'], 'existing.jpg')

    @patch.object(face_app, 'PROMO_CODE', 'MASTER')
    def test_master_promo_is_case_insensitive_and_server_configured(self):
        rejected = self.client.post(
            '/check-promo-code', json={'promo_code': 'not-master'}
        )
        self.assertFalse(rejected.get_json()['success'])
        accepted = self.client.post('/check-promo-code', json={'promo_code': 'master'})
        self.assertTrue(accepted.get_json()['success'])
        with self.client.session_transaction() as session:
            self.assertTrue(session['free_analysis'])
            self.assertGreater(session['free_analysis_expires_at'], int(face_app.time.time()))
            self.assertGreaterEqual(
                session['ai_authorized_until'], int(face_app.time.time())
            )

    @patch.object(face_app, 'PROMO_CODE', 'MASTER')
    @patch.object(face_app, 'run_analysis', return_value=SAMPLE_RESULT)
    def test_master_grant_authorizes_exactly_one_free_analysis(self, analysis_mock):
        with self.client.session_transaction() as session:
            session['uploaded_file'] = 'existing.jpg'
            session['language'] = 'en'

        accepted = self.client.post(
            '/check-promo-code', json={'promo_code': ' MaStEr '}
        )
        self.assertEqual(accepted.status_code, 200)
        self.assertTrue(accepted.get_json()['success'])

        first = self.client.post('/free-analysis')
        second = self.client.post('/free-analysis')

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 403)
        analysis_mock.assert_called_once_with('existing.jpg', 'en')

    @patch.object(face_app, 'PROMO_CODE', 'MASTER')
    def test_promo_attempts_remain_rate_limited(self):
        for _ in range(10):
            response = self.client.post(
                '/check-promo-code', json={'promo_code': 'invalid'}
            )
            self.assertEqual(response.status_code, 200)

        limited = self.client.post(
            '/check-promo-code', json={'promo_code': 'MASTER'}
        )
        self.assertEqual(limited.status_code, 429)

    @patch.object(face_app, 'translate_text', return_value='Bună')
    def test_translation_requires_authorization_and_caps_input(self, translate_mock):
        self.assertEqual(
            self.client.post('/translate', json={'text': 'Hello', 'language': 'ro'}).status_code,
            403,
        )
        with self.client.session_transaction() as session:
            session['ai_authorized_until'] = int(face_app.time.time()) + 60
        oversized = self.client.post(
            '/translate',
            json={'text': 'x' * (face_app.MAX_TRANSLATION_CHARACTERS + 1), 'language': 'ro'},
        )
        self.assertEqual(oversized.status_code, 413)
        translated = self.client.post(
            '/translate', json={'text': 'Hello', 'language': 'ro'}
        )
        self.assertEqual(translated.status_code, 200)
        translate_mock.assert_called_once_with('Hello', 'ro')

    def test_translation_is_rate_limited(self):
        with self.client.session_transaction() as session:
            session['ai_authorized_until'] = int(face_app.time.time()) + 60
        with patch.object(face_app, 'translate_text', return_value='ok'):
            for _ in range(20):
                self.assertEqual(
                    self.client.post(
                        '/translate', json={'text': 'Hello', 'language': 'en'}
                    ).status_code,
                    200,
                )
            self.assertEqual(
                self.client.post(
                    '/translate', json={'text': 'Hello', 'language': 'en'}
                ).status_code,
                429,
            )

    def test_react_shell_replaces_legacy_frontend_dependencies(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'/static/react/assets/', response.data)
        self.assertNotIn(b'bootstrap', response.data.lower())
        self.assertNotIn(b'font-awesome', response.data.lower())

    def test_face_detection_dependency_is_complete(self):
        self.assertTrue(hasattr(face_app.cv2, 'CascadeClassifier'))
        self.assertTrue(hasattr(face_app.cv2, 'data'))

    def test_application_refuses_to_start_without_session_secret(self):
        environment = os.environ.copy()
        environment.pop('SESSION_SECRET', None)
        result = subprocess.run(
            [sys.executable, '-c', 'import app'],
            cwd=os.path.dirname(__file__),
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('SESSION_SECRET must be set', result.stderr)

    def test_master_promo_is_enabled_only_in_development_workflow(self):
        replit_config = tomllib.loads(
            Path(__file__).with_name('.replit').read_text(encoding='utf-8')
        )
        workflows = replit_config['workflows']['workflow']
        start_workflow = next(
            workflow
            for workflow in workflows
            if workflow['name'] == 'Start application'
        )
        development_commands = [
            task['args']
            for task in start_workflow['tasks']
            if task['task'] == 'shell.exec'
        ]
        self.assertTrue(
            any('PROMO_CODE=MASTER' in command for command in development_commands),
            'The Start application development workflow must enable PROMO_CODE=MASTER',
        )

        deployment_config = repr(replit_config['deployment'])
        self.assertNotIn(
            'PROMO_CODE',
            deployment_config,
            'Production deployment configuration must not set PROMO_CODE',
        )
        self.assertNotIn(
            'MASTER',
            deployment_config,
            'Production deployment configuration must never expose the MASTER promo code',
        )

    @patch.dict(os.environ, {
        'AI_INTEGRATIONS_OPENAI_API_KEY': 'managed-test-key',
        'AI_INTEGRATIONS_OPENAI_BASE_URL': 'https://managed-ai.example.test',
    })
    @patch.object(openai_service, 'OpenAI')
    def test_replit_managed_openai_credentials_are_used(self, client_mock):
        openai_service.get_ai_client()
        client_mock.assert_called_once_with(
            api_key='managed-test-key',
            base_url='https://managed-ai.example.test',
        )

    @patch.object(openai_service, 'encode_image', return_value='encoded-image')
    @patch.object(openai_service, 'get_ai_client')
    def test_exhausted_openai_credits_return_actionable_error(self, client_mock, _encode_mock):
        client_mock.return_value.chat.completions.create.side_effect = RuntimeError(
            'credit_balance_exhausted: no credits remaining'
        )
        result = openai_service.analyze_face_with_ai('/missing.jpg')
        self.assertEqual(result['error'], 'Analysis failed')
        self.assertIn('no OpenAI credits remaining', result['message'])


if __name__ == '__main__':
    unittest.main()
