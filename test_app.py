import io
import os
import unittest
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
        self.client = face_app.app.test_client()

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
        analyzed = self.client.post('/free-analysis')
        self.assertEqual(analyzed.status_code, 200)
        self.assertNotIn('pdf_path', analyzed.get_json())
        results = self.client.get('/success')
        self.assertEqual(results.status_code, 200)
        self.assertIn(b'Executive Summary', results.data)
        download = self.client.get('/download-pdf')
        self.assertEqual(download.status_code, 200)
        self.assertEqual(download.mimetype, 'application/pdf')
        self.assertTrue(download.data.startswith(b'%PDF'))
        self.assertEqual(self.client.get('/download-pdf').status_code, 404)

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
        self.assertEqual(response.status_code, 405)

    def test_face_detection_dependency_is_complete(self):
        self.assertTrue(hasattr(face_app.cv2, 'CascadeClassifier'))
        self.assertTrue(hasattr(face_app.cv2, 'data'))

    @patch.dict(os.environ, {
        'OPENAI_API_KEY': 'test-key',
        'AI_INTEGRATIONS_OPENAI_API_KEY': '',
        'AI_INTEGRATIONS_OPENAI_BASE_URL': '',
    })
    @patch.object(openai_service, 'OpenAI')
    def test_standard_openai_credentials_are_supported(self, client_mock):
        openai_service.get_ai_client()
        client_mock.assert_called_once_with(api_key='test-key')

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