import io
import os
import tempfile
import unittest
from unittest.mock import patch

from PIL import Image

import app as face_app


def valid_image():
    stream = io.BytesIO()
    Image.new('RGB', (512, 512), 'tan').save(stream, format='JPEG')
    stream.seek(0)
    return stream


class MobileApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary_directory = tempfile.TemporaryDirectory()
        face_app.app.config.update(
            TESTING=True,
            SECRET_KEY='mobile-api-test-secret',
            MOBILE_API_DATABASE=os.path.join(self.temporary_directory.name, 'mobile.sqlite3'),
        )
        face_app._rate_limit_events.clear()
        self.client = face_app.app.test_client()
        self.token = self.client.post('/api/mobile/session').get_json()['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def tearDown(self):
        self.temporary_directory.cleanup()

    def test_mobile_routes_require_bearer_authorization(self):
        for method, path in (
            ('post', '/api/mobile/upload'),
            ('post', '/api/mobile/promo'),
            ('post', '/api/mobile/analyze'),
            ('get', '/api/mobile/report'),
            ('post', '/api/mobile/cancel'),
        ):
            response = getattr(self.client, method)(path)
            self.assertEqual(response.status_code, 401, path)

    def test_bad_file_types_and_malformed_images_are_rejected_without_ai(self):
        with patch.object(face_app, 'analyze_face_with_ai') as ai_mock:
            bad_type = self.client.post(
                '/api/mobile/upload',
                headers=self.headers,
                data={'file': (io.BytesIO(b'not an image'), 'portrait.txt'), 'language': 'en'},
                content_type='multipart/form-data',
            )
            self.assertEqual(bad_type.status_code, 400)
            malformed = self.client.post(
                '/api/mobile/upload',
                headers=self.headers,
                data={'file': (io.BytesIO(b'not an image'), 'portrait.jpg'), 'language': 'en'},
                content_type='multipart/form-data',
            )
            self.assertEqual(malformed.status_code, 400)
            ai_mock.assert_not_called()

    @patch.object(face_app, 'PROMO_CODE', 'MOBILE-TEST')
    @patch.object(face_app, 'generate_analysis_pdf')
    @patch.object(face_app, 'analyze_face_with_ai', return_value={
        'executive_summary': 'A reflective summary.',
    })
    @patch.object(face_app, 'detect_face_landmarks', return_value={'face_detected': True})
    def test_promo_grant_funds_one_analysis_and_report_is_private(
        self, _detect_mock, ai_mock, pdf_mock
    ):
        def write_test_pdf(_result, report_path, _language):
            with open(report_path, 'wb') as report:
                report.write(b'%PDF-1.4 mobile test report')

        pdf_mock.side_effect = write_test_pdf
        uploaded = self.client.post(
            '/api/mobile/upload',
            headers=self.headers,
            data={'file': (valid_image(), 'portrait.jpg'), 'language': 'en'},
            content_type='multipart/form-data',
        )
        self.assertEqual(uploaded.status_code, 200)
        accepted = self.client.post(
            '/api/mobile/promo', headers=self.headers, json={'promo_code': 'mobile-test'}
        )
        self.assertTrue(accepted.get_json()['success'])
        first = self.client.post('/api/mobile/analyze', headers=self.headers)
        second = self.client.post('/api/mobile/analyze', headers=self.headers)
        self.assertEqual(first.status_code, 200)
        self.assertEqual(first.get_json()['analysis']['executive_summary'], 'A reflective summary.')
        self.assertEqual(second.status_code, 403)
        ai_mock.assert_called_once()
        pdf_mock.assert_called_once()
        report = self.client.get('/api/mobile/report', headers=self.headers)
        self.assertEqual(report.status_code, 200)
        self.assertEqual(report.mimetype, 'application/pdf')
        self.assertTrue(report.data.startswith(b'%PDF'))

    @patch.object(face_app, 'PROMO_CODE', '')
    def test_unconfigured_promo_never_issues_a_mobile_grant(self):
        result = self.client.post(
            '/api/mobile/promo', headers=self.headers, json={'promo_code': 'anything'}
        )
        self.assertFalse(result.get_json()['success'])
        self.assertEqual(
            self.client.post('/api/mobile/analyze', headers=self.headers).status_code,
            403,
        )

    @patch.dict(os.environ, {'REPLIT_EXPO_DEV_DOMAIN': 'expo.example.test'})
    def test_expo_origin_has_scoped_mobile_and_page_cors(self):
        origin = 'https://expo.example.test'
        session = self.client.post('/api/mobile/session', headers={'Origin': origin})
        self.assertEqual(session.status_code, 201)
        self.assertEqual(session.headers.get('Access-Control-Allow-Origin'), origin)

        preflight = self.client.options(
            '/api/mobile/upload',
            headers={
                'Origin': origin,
                'Access-Control-Request-Method': 'POST',
                'Access-Control-Request-Headers': 'authorization,content-type',
            },
        )
        self.assertEqual(preflight.status_code, 204)
        self.assertEqual(preflight.headers.get('Access-Control-Allow-Origin'), origin)
        self.assertEqual(preflight.headers.get('Access-Control-Allow-Methods'), 'POST')
        self.assertIn('authorization', preflight.headers.get('Access-Control-Allow-Headers', '').lower())

        page = self.client.get('/api/page', headers={'Origin': origin})
        self.assertEqual(page.status_code, 200)
        self.assertEqual(page.headers.get('Access-Control-Allow-Origin'), origin)
        unrelated = self.client.get('/api/healthz', headers={'Origin': origin})
        self.assertNotIn('Access-Control-Allow-Origin', unrelated.headers)

    @patch.dict(os.environ, {'REPLIT_EXPO_DEV_DOMAIN': 'expo.example.test'})
    def test_unconfigured_origins_remain_blocked_for_mobile_state_changes(self):
        response = self.client.post(
            '/api/mobile/session', headers={'Origin': 'https://attacker.example'}
        )
        self.assertEqual(response.status_code, 403)
        self.assertNotIn('Access-Control-Allow-Origin', response.headers)

    def test_mobile_session_creation_is_rate_limited(self):
        face_app._rate_limit_events.clear()
        for _ in range(10):
            self.assertEqual(self.client.post('/api/mobile/session').status_code, 201)
        limited = self.client.post('/api/mobile/session')
        self.assertEqual(limited.status_code, 429)


if __name__ == '__main__':
    unittest.main()