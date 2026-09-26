import io
import json
import os
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image
import psycopg2
from psycopg2 import sql

import app as face_app


def valid_image():
    stream = io.BytesIO()
    Image.new('RGB', (512, 512), 'tan').save(stream, format='JPEG')
    stream.seek(0)
    return stream


def revenuecat_payload(*transactions, status='owned', product_app_id='test-store-app'):
    return [
        {
            'object': 'purchase',
            'id': f'purchase-{transaction}',
            'product_id': 'prod-ancient-wisdom-consumable',
            'status': status,
            'store_purchase_identifier': transaction,
            'revenuecat_product': {
                'object': 'product',
                'id': 'prod-ancient-wisdom-consumable',
                'store_identifier': 'ancient_wisdom_report',
                'app_id': product_app_id,
                'type': 'consumable',
                'one_time': {'is_consumable': True},
            },
        }
        for transaction in transactions
    ]


class MobileApiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_database_url = os.environ.get('MOBILE_API_TEST_DATABASE_URL')
        if not cls.test_database_url:
            raise unittest.SkipTest(
                'Set MOBILE_API_TEST_DATABASE_URL to a dedicated PostgreSQL test database'
            )
        cls.test_schema = f'mobile_api_test_{uuid.uuid4().hex}'
        with psycopg2.connect(cls.test_database_url) as connection:
            with connection.cursor() as cursor:
                cursor.execute(sql.SQL('CREATE SCHEMA {}').format(sql.Identifier(cls.test_schema)))
        options = f'-c search_path={cls.test_schema}'
        with psycopg2.connect(cls.test_database_url, options=options) as connection:
            with connection.cursor() as cursor:
                schema_sql = Path(__file__).parent / 'sql' / 'mobile.sql'
                cursor.execute(schema_sql.read_text(encoding='utf-8'))

    @classmethod
    def tearDownClass(cls):
        if getattr(cls, 'test_database_url', None) and getattr(cls, 'test_schema', None):
            with psycopg2.connect(cls.test_database_url) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        sql.SQL('DROP SCHEMA {} CASCADE').format(sql.Identifier(cls.test_schema))
                    )

    def setUp(self):
        face_app.app.config.update(
            TESTING=True,
            SECRET_KEY='mobile-api-test-secret',
            MOBILE_API_DATABASE_URL=self.test_database_url,
            MOBILE_API_DATABASE_SCHEMA=self.test_schema,
        )
        with face_app.mobile_db() as connection:
            connection.execute(
                'TRUNCATE mobile_purchase_redemptions, mobile_sessions, mobile_devices'
            )
        face_app._rate_limit_events.clear()
        self.client = face_app.app.test_client()
        self.session_response = self.client.post('/api/mobile/session').get_json()
        self.token = self.session_response['access_token']
        self.headers = {'Authorization': f'Bearer {self.token}'}

    def test_mobile_routes_require_bearer_authorization(self):
        for method, path in (
            ('post', '/api/mobile/upload'),
            ('post', '/api/mobile/promo'),
            ('post', '/api/mobile/redeem'),
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
        self.assertEqual(second.status_code, 400)
        ai_mock.assert_called_once()
        pdf_mock.assert_called_once()
        report = self.client.get('/api/mobile/report', headers=self.headers)
        self.assertEqual(report.status_code, 200)
        self.assertEqual(report.mimetype, 'application/pdf')
        self.assertTrue(report.data.startswith(b'%PDF'))
        with face_app.mobile_db() as connection:
            row = connection.execute(
                'SELECT report_id FROM mobile_sessions WHERE token_hash = ?',
                (face_app.mobile_token_hash(self.token),),
            ).fetchone()
        os.remove(face_app.report_path(row['report_id']))
        restored_report = self.client.get('/api/mobile/report', headers=self.headers)
        self.assertEqual(restored_report.status_code, 200)
        self.assertTrue(restored_report.data.startswith(b'%PDF'))
        self.assertEqual(pdf_mock.call_count, 2)

    @patch.object(face_app, 'PROMO_CODE', '')
    def test_unconfigured_promo_never_issues_a_mobile_grant(self):
        result = self.client.post(
            '/api/mobile/promo', headers=self.headers, json={'promo_code': 'anything'}
        )
        self.assertFalse(result.get_json()['success'])
        self.assertEqual(
            self.client.post('/api/mobile/analyze', headers=self.headers).status_code,
            400,
        )

    def test_mobile_session_exposes_stable_revenuecat_app_user_id(self):
        app_user_id = self.session_response['rc_app_user_id']
        self.assertRegex(
            app_user_id,
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        )
        with face_app.mobile_db() as connection:
            stored = connection.execute(
                '''SELECT rc_app_user_id, device_token_hash FROM mobile_sessions
                   WHERE token_hash = ?''',
                (face_app.mobile_token_hash(self.token),),
            ).fetchone()
        self.assertEqual(stored['rc_app_user_id'], app_user_id)
        device_token = self.session_response['device_token']
        self.assertTrue(device_token)
        self.assertEqual(stored['device_token_hash'], face_app.mobile_token_hash(device_token))

    def test_device_token_recovers_identity_after_cancel_and_session_expiry(self):
        device_token = self.session_response['device_token']
        app_user_id = self.session_response['rc_app_user_id']

        canceled = self.client.post('/api/mobile/cancel', headers=self.headers)
        self.assertEqual(canceled.status_code, 200)
        after_cancel = self.client.post(
            '/api/mobile/session',
            json={'device_token': device_token, 'rc_app_user_id': 'forged-customer'},
        )
        self.assertEqual(after_cancel.status_code, 201)
        self.assertEqual(after_cancel.get_json()['rc_app_user_id'], app_user_id)
        self.assertEqual(after_cancel.get_json()['device_token'], device_token)

        current_token = after_cancel.get_json()['access_token']
        with face_app.mobile_db() as connection:
            connection.execute(
                'UPDATE mobile_sessions SET expires_at = 0 WHERE token_hash = ?',
                (face_app.mobile_token_hash(current_token),),
            )
        after_expiry = self.client.post(
            '/api/mobile/session', json={'device_token': device_token}
        )
        self.assertEqual(after_expiry.status_code, 201)
        self.assertEqual(after_expiry.get_json()['rc_app_user_id'], app_user_id)
        with face_app.mobile_db() as connection:
            self.assertEqual(
                connection.execute('SELECT COUNT(*) FROM mobile_devices').fetchone()[0],
                1,
            )
            self.assertEqual(
                connection.execute('SELECT COUNT(*) FROM mobile_sessions').fetchone()[0],
                1,
            )

    def test_invalid_device_token_cannot_create_or_spoof_a_customer_identity(self):
        original_identity = self.session_response['rc_app_user_id']
        invalid = self.client.post(
            '/api/mobile/session',
            json={
                'device_token': 'not-a-valid-device-credential',
                'rc_app_user_id': 'forged-customer',
            },
        )
        self.assertEqual(invalid.status_code, 401)
        with face_app.mobile_db() as connection:
            self.assertEqual(
                connection.execute('SELECT COUNT(*) FROM mobile_devices').fetchone()[0],
                1,
            )
            self.assertEqual(
                connection.execute('SELECT COUNT(*) FROM mobile_sessions').fetchone()[0],
                1,
            )

        spoofed_id = self.client.post(
            '/api/mobile/session', json={'rc_app_user_id': 'forged-customer'}
        )
        self.assertEqual(spoofed_id.status_code, 201)
        self.assertNotEqual(spoofed_id.get_json()['rc_app_user_id'], 'forged-customer')
        self.assertNotEqual(spoofed_id.get_json()['rc_app_user_id'], original_identity)

    def test_missing_database_fails_closed_without_creating_a_session(self):
        face_app.app.config['MOBILE_API_DATABASE_URL'] = None
        with patch.dict(os.environ, {'DATABASE_URL': ''}):
            response = self.client.post('/api/mobile/session')
        self.assertEqual(response.status_code, 503)

    @patch.dict(os.environ, {'REVENUECAT_PRODUCT_ID': 'ancient_wisdom_report'})
    def test_revenuecat_bridge_invokes_ts_helper_without_shell_and_parses_json(self):
        payload = revenuecat_payload('bridge-transaction')
        with patch.object(
            face_app.subprocess,
            'run',
            return_value=SimpleNamespace(returncode=0, stdout=json.dumps(payload)),
        ) as run:
            result = face_app.revenuecat_customer_purchases('project-id', 'customer-id')

        self.assertEqual(result, payload)
        args, kwargs = run.call_args
        self.assertTrue(args[0][0].endswith('scripts/node_modules/.bin/tsx'))
        self.assertTrue(args[0][1].endswith('scripts/src/revenueCatPurchases.ts'))
        self.assertEqual(
            args[0][2:],
            ['project-id', 'customer-id', 'ancient_wisdom_report'],
        )
        self.assertNotIn('shell', kwargs)
        self.assertTrue(kwargs['capture_output'])

    def test_revenuecat_catalog_products_are_environment_scoped(self):
        test_store_purchases = revenuecat_payload(
            'test-transaction', product_app_id='test-store-app'
        )
        native_purchases = revenuecat_payload(
            'native-transaction', product_app_id='native-ios-app'
        )
        self.assertEqual(
            face_app.valid_revenuecat_purchase_transactions(
                test_store_purchases, 'ancient_wisdom_report', 'test-store-app',
                production=False,
            ),
            ['test-transaction'],
        )
        self.assertEqual(
            face_app.valid_revenuecat_purchase_transactions(
                test_store_purchases, 'ancient_wisdom_report', 'test-store-app',
                production=True,
            ),
            [],
        )
        self.assertEqual(
            face_app.valid_revenuecat_purchase_transactions(
                native_purchases, 'ancient_wisdom_report', 'test-store-app',
                production=False,
            ),
            [],
        )
        self.assertEqual(
            face_app.valid_revenuecat_purchase_transactions(
                native_purchases, 'ancient_wisdom_report', 'test-store-app',
                production=True,
            ),
            ['native-transaction'],
        )

    @patch.dict(os.environ, {
        'REVENUECAT_PROJECT_ID': 'project-test',
        'REVENUECAT_PRODUCT_ID': 'ancient_wisdom_report',
        'REVENUECAT_TEST_STORE_APP_ID': 'test-store-app',
        'REPLIT_DEPLOYMENT': '1',
    })
    def test_production_redemption_rejects_test_store_and_accepts_native_purchase(self):
        with patch.object(
            face_app,
            'revenuecat_customer_purchases',
            return_value=revenuecat_payload(
                'test-transaction', product_app_id='test-store-app'
            ),
        ):
            test_purchase = self.client.post('/api/mobile/redeem', headers=self.headers)
        self.assertEqual(test_purchase.status_code, 402)

        with patch.object(
            face_app,
            'revenuecat_customer_purchases',
            return_value=revenuecat_payload(
                'native-transaction', product_app_id='native-ios-app'
            ),
        ):
            native_purchase = self.client.post('/api/mobile/redeem', headers=self.headers)
        self.assertEqual(native_purchase.status_code, 200)
        with face_app.mobile_db() as connection:
            redeemed = connection.execute(
                'SELECT transaction_id FROM mobile_purchase_redemptions'
            ).fetchone()
        self.assertEqual(redeemed['transaction_id'], 'native-transaction')

    @patch.dict(os.environ, {
        'REVENUECAT_PROJECT_ID': 'project-test',
        'REVENUECAT_PRODUCT_ID': 'ancient_wisdom_report',
        'REVENUECAT_TEST_STORE_APP_ID': 'test-store-app',
        'REPLIT_DEPLOYMENT': '',
    })
    def test_redeem_verifies_server_customer_and_transaction_is_globally_unique(self):
        purchases = revenuecat_payload('store-transaction-123')
        with patch.object(
            face_app, 'revenuecat_customer_purchases', return_value=purchases
        ) as provider:
            redeemed = self.client.post(
                '/api/mobile/redeem',
                headers=self.headers,
                json={
                    'rc_app_user_id': 'attacker-customer',
                    'transaction_id': 'attacker-transaction',
                    'entitlement': 'premium',
                },
            )
        self.assertEqual(redeemed.status_code, 200)
        self.assertTrue(redeemed.get_json()['free_analysis'])
        provider.assert_called_once_with(
            'project-test', self.session_response['rc_app_user_id']
        )
        with face_app.mobile_db() as connection:
            grant = connection.execute(
                'SELECT grant_issued, grant_used FROM mobile_sessions WHERE token_hash = ?',
                (face_app.mobile_token_hash(self.token),),
            ).fetchone()
        self.assertEqual((grant['grant_issued'], grant['grant_used']), (1, 0))

        other = self.client.post('/api/mobile/session').get_json()
        with patch.object(face_app, 'revenuecat_customer_purchases', return_value=purchases):
            duplicate = self.client.post(
                '/api/mobile/redeem',
                headers={'Authorization': f"Bearer {other['access_token']}"},
            )
        self.assertEqual(duplicate.status_code, 409)
        with face_app.mobile_db() as connection:
            self.assertEqual(
                connection.execute(
                    'SELECT COUNT(*) FROM mobile_purchase_redemptions'
                ).fetchone()[0],
                1,
            )

    @patch.dict(os.environ, {
        'REVENUECAT_PROJECT_ID': 'project-test',
        'REVENUECAT_PRODUCT_ID': 'ancient_wisdom_report',
        'REVENUECAT_TEST_STORE_APP_ID': 'test-store-app',
        'REPLIT_DEPLOYMENT': '',
    })
    def test_unavailable_or_refunded_provider_purchase_does_not_issue_grant(self):
        with patch.object(face_app, 'revenuecat_customer_purchases', return_value=None):
            unavailable = self.client.post('/api/mobile/redeem', headers=self.headers)
        self.assertEqual(unavailable.status_code, 503)

        with patch.object(
            face_app, 'revenuecat_customer_purchases',
            return_value=revenuecat_payload('refunded-transaction', status='refunded'),
        ):
            refunded = self.client.post('/api/mobile/redeem', headers=self.headers)
        self.assertEqual(refunded.status_code, 402)
        with face_app.mobile_db() as connection:
            grant = connection.execute(
                'SELECT grant_issued FROM mobile_sessions WHERE token_hash = ?',
                (face_app.mobile_token_hash(self.token),),
            ).fetchone()
        self.assertEqual(grant['grant_issued'], 0)

    @patch.dict(os.environ, {
        'REVENUECAT_PROJECT_ID': 'project-test',
        'REVENUECAT_PRODUCT_ID': 'ancient_wisdom_report',
        'REVENUECAT_TEST_STORE_APP_ID': 'test-store-app',
        'REPLIT_DEPLOYMENT': '',
    })
    def test_concurrent_redemption_cannot_redeem_a_transaction_twice(self):
        other = self.client.post('/api/mobile/session').get_json()
        purchases = revenuecat_payload('concurrent-transaction')

        def redeem(token):
            with face_app.app.test_client() as client:
                return client.post(
                    '/api/mobile/redeem',
                    headers={'Authorization': f'Bearer {token}'},
                ).status_code

        with patch.object(face_app, 'revenuecat_customer_purchases', return_value=purchases):
            with ThreadPoolExecutor(max_workers=2) as executor:
                statuses = list(executor.map(
                    redeem, (self.token, other['access_token'])
                ))
        self.assertCountEqual(statuses, [200, 409])
        with face_app.mobile_db() as connection:
            self.assertEqual(
                connection.execute(
                    'SELECT COUNT(*) FROM mobile_purchase_redemptions '
                    'WHERE transaction_id = ?',
                    ('concurrent-transaction',),
                ).fetchone()[0],
                1,
            )

    @patch.dict(os.environ, {
        'REVENUECAT_PROJECT_ID': 'project-test',
        'REVENUECAT_PRODUCT_ID': 'ancient_wisdom_report',
        'REVENUECAT_TEST_STORE_APP_ID': 'test-store-app',
        'REPLIT_DEPLOYMENT': '',
    })
    def test_successive_consumable_purchases_issue_new_grants(self):
        purchases = revenuecat_payload('purchase-one', 'purchase-two')
        with patch.object(face_app, 'revenuecat_customer_purchases', return_value=purchases):
            first = self.client.post('/api/mobile/redeem', headers=self.headers)
        self.assertEqual(first.status_code, 200)

        # A completed/failed analysis consumes the current grant; another purchase can fund one more.
        with face_app.mobile_db() as connection:
            connection.execute(
                'UPDATE mobile_sessions SET grant_used = 1 WHERE token_hash = ?',
                (face_app.mobile_token_hash(self.token),),
            )
        with patch.object(face_app, 'revenuecat_customer_purchases', return_value=purchases):
            second = self.client.post('/api/mobile/redeem', headers=self.headers)
        self.assertEqual(second.status_code, 200)
        with face_app.mobile_db() as connection:
            redemptions = connection.execute(
                '''SELECT transaction_id FROM mobile_purchase_redemptions
                   WHERE token_hash = ? ORDER BY redeemed_at, transaction_id''',
                (face_app.mobile_token_hash(self.token),),
            ).fetchall()
            grant = connection.execute(
                'SELECT grant_issued, grant_used FROM mobile_sessions WHERE token_hash = ?',
                (face_app.mobile_token_hash(self.token),),
            ).fetchone()
        self.assertCountEqual(
            [row['transaction_id'] for row in redemptions],
            ['purchase-one', 'purchase-two'],
        )
        self.assertEqual((grant['grant_issued'], grant['grant_used']), (1, 0))

    def upload_portrait_for_analysis(self):
        return self.client.post(
            '/api/mobile/upload',
            headers=self.headers,
            data={'file': (valid_image(), 'portrait.jpg'), 'language': 'en'},
            content_type='multipart/form-data',
        )

    def issue_test_grant(self):
        with patch.object(face_app, 'PROMO_CODE', 'TEST-PROMO'):
            return self.client.post(
                '/api/mobile/promo',
                headers=self.headers,
                json={'promo_code': 'test-promo'},
            )

    def test_no_face_failure_releases_grant_for_a_retry(self):
        self.assertEqual(self.issue_test_grant().status_code, 200)
        self.assertEqual(self.upload_portrait_for_analysis().status_code, 200)
        with patch.object(face_app, 'detect_face_landmarks', return_value=None):
            failed = self.client.post('/api/mobile/analyze', headers=self.headers)
        self.assertEqual(failed.status_code, 422)
        with face_app.mobile_db() as connection:
            grant = connection.execute(
                'SELECT grant_used, grant_expires_at FROM mobile_sessions WHERE token_hash = ?',
                (face_app.mobile_token_hash(self.token),),
            ).fetchone()
        self.assertEqual(grant['grant_used'], 0)
        self.assertGreater(grant['grant_expires_at'], int(time.time()))

        face_app._rate_limit_events.clear()
        self.assertEqual(self.upload_portrait_for_analysis().status_code, 200)
        def write_pdf(_result, path, _language):
            with open(path, 'wb') as report:
                report.write(b'%PDF')

        with patch.object(face_app, 'detect_face_landmarks', return_value={'face_detected': True}), \
             patch.object(face_app, 'analyze_face_with_ai', return_value={
                 'executive_summary': 'Retry succeeded.',
             }), \
             patch.object(face_app, 'generate_analysis_pdf', side_effect=write_pdf):
            retried = self.client.post('/api/mobile/analyze', headers=self.headers)
        self.assertEqual(retried.status_code, 200)

    def test_ai_and_pdf_failures_release_the_analysis_grant(self):
        self.assertEqual(self.issue_test_grant().status_code, 200)
        self.assertEqual(self.upload_portrait_for_analysis().status_code, 200)
        with patch.object(face_app, 'detect_face_landmarks', return_value={'face_detected': True}), \
             patch.object(face_app, 'analyze_face_with_ai', return_value={
                 'error': True,
                 'message': 'AI unavailable',
             }):
            failed_ai = self.client.post('/api/mobile/analyze', headers=self.headers)
        self.assertEqual(failed_ai.status_code, 503)
        with face_app.mobile_db() as connection:
            self.assertEqual(
                connection.execute(
                    'SELECT grant_used FROM mobile_sessions WHERE token_hash = ?',
                    (face_app.mobile_token_hash(self.token),),
                ).fetchone()['grant_used'],
                0,
            )

        face_app._rate_limit_events.clear()
        self.assertEqual(self.upload_portrait_for_analysis().status_code, 200)
        with patch.object(face_app, 'detect_face_landmarks', return_value={'face_detected': True}), \
             patch.object(face_app, 'analyze_face_with_ai', return_value={
                 'executive_summary': 'Analysis succeeded.',
             }), \
             patch.object(face_app, 'generate_analysis_pdf', side_effect=RuntimeError('PDF failure')):
            failed_pdf = self.client.post('/api/mobile/analyze', headers=self.headers)
        self.assertEqual(failed_pdf.status_code, 500)
        with face_app.mobile_db() as connection:
            self.assertEqual(
                connection.execute(
                    'SELECT grant_used FROM mobile_sessions WHERE token_hash = ?',
                    (face_app.mobile_token_hash(self.token),),
                ).fetchone()['grant_used'],
                0,
            )

    def test_concurrent_analysis_claim_runs_ai_once(self):
        self.assertEqual(self.issue_test_grant().status_code, 200)
        self.assertEqual(self.upload_portrait_for_analysis().status_code, 200)
        analysis_started = Event()
        allow_analysis_to_finish = Event()

        def analyze_once(*_args):
            analysis_started.set()
            if not allow_analysis_to_finish.wait(timeout=10):
                raise TimeoutError('Test did not release analysis worker')
            return {'executive_summary': 'Completed once.'}

        def run_analysis():
            with face_app.app.test_client() as client:
                return client.post(
                    '/api/mobile/analyze',
                    headers={'Authorization': f'Bearer {self.token}'},
                )

        def write_test_pdf(_result, path, _language):
            with open(path, 'wb') as report:
                report.write(b'%PDF')

        with patch.object(face_app, 'detect_face_landmarks', return_value={'face_detected': True}), \
             patch.object(face_app, 'analyze_face_with_ai', side_effect=analyze_once) as ai_mock, \
             patch.object(face_app, 'generate_analysis_pdf', side_effect=write_test_pdf):
            with ThreadPoolExecutor(max_workers=1) as executor:
                future = executor.submit(run_analysis)
                try:
                    self.assertTrue(analysis_started.wait(timeout=5))
                    concurrent = self.client.post('/api/mobile/analyze', headers=self.headers)
                    self.assertEqual(concurrent.status_code, 409)
                finally:
                    allow_analysis_to_finish.set()
                completed = future.result(timeout=10)
        self.assertEqual(completed.status_code, 200)
        ai_mock.assert_called_once()

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