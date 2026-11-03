import io
import json
import os
import unittest
from unittest.mock import patch

from PIL import Image

import app as face_app
import file_store


def valid_image():
    stream = io.BytesIO()
    Image.new('RGB', (512, 512), 'tan').save(stream, format='JPEG')
    stream.seek(0)
    return stream


class DurableFileStoreTest(unittest.TestCase):
    """Uploads must survive a request landing on a fresh serverless instance."""

    @classmethod
    def setUpClass(cls):
        cls.database_url = os.environ.get('MOBILE_API_TEST_DATABASE_URL')
        if not cls.database_url:
            raise unittest.SkipTest('Set MOBILE_API_TEST_DATABASE_URL to a dedicated PostgreSQL test database')

    def setUp(self):
        self.env = patch.dict(os.environ, {'FILE_STORE': 'postgres', 'DATABASE_URL': self.database_url})
        self.env.start()
        face_app.app.config['TESTING'] = True
        self.client = face_app.app.test_client()

    def tearDown(self):
        self.env.stop()

    def test_upload_is_restored_after_local_temp_is_lost(self):
        response = self.client.post(
            '/api/upload',
            data={'file': (valid_image(), 'portrait.jpg'), 'language': 'en'},
            content_type='multipart/form-data',
            headers={'Origin': 'http://localhost'},
        )
        self.assertEqual(response.status_code, 200)
        path = face_app.uploaded_path(response.get_json()['filename'])
        os.remove(path)  # a different instance has an empty /tmp
        self.assertTrue(file_store.fetch(path))
        with Image.open(path) as image:
            self.assertEqual(image.size, (512, 512))
        face_app.safe_remove(path)
        self.assertFalse(file_store.fetch(path))

    def test_saved_analysis_is_loaded_from_storage(self):
        report_id = 'analysis_test.pdf'
        path = face_app.analysis_path(report_id)
        with open(path, 'w', encoding='utf-8') as handle:
            json.dump({'executive_summary': 'stored'}, handle)
        file_store.save(path)
        os.remove(path)
        self.assertEqual(face_app.load_analysis(report_id), {'executive_summary': 'stored'})
        face_app.safe_remove(path)

    def test_store_is_inert_without_configuration(self):
        with patch.dict(os.environ, {'FILE_STORE': ''}):
            self.assertFalse(file_store.fetch(face_app.uploaded_path('missing.jpg')))
            file_store.save('/nonexistent/path')  # no-op, no error


class RevenueCatApiTest(unittest.TestCase):
    def fake_urlopen(self, pages):
        class Response(io.BytesIO):
            def __enter__(self):
                return self

            def __exit__(self, *args):
                return False

        def urlopen(request, timeout):
            self.assertEqual(request.headers['Authorization'], 'Bearer sk_test')
            path = request.full_url.replace(face_app.REVENUECAT_API_BASE, '')
            return Response(json.dumps(pages[path]).encode())
        return urlopen

    @patch.dict(os.environ, {'REVENUECAT_SECRET_API_KEY': 'sk_test', 'REVENUECAT_PRODUCT_ID': 'report',
                             'REVENUECAT_TEST_STORE_APP_ID': 'test-app', 'REPLIT_DEPLOYMENT': '', 'VERCEL_ENV': 'production'})
    def test_rest_api_returns_only_production_purchases_of_the_product(self):
        pages = {
            '/v2/projects/proj/products?limit=100': {'items': [
                {'id': 'prod_native', 'store_identifier': 'report', 'app_id': 'ios-app'},
                {'id': 'prod_test', 'store_identifier': 'report', 'app_id': 'test-app'},
                {'id': 'prod_other', 'store_identifier': 'other', 'app_id': 'ios-app'},
            ], 'next_page': None},
            '/v2/projects/proj/customers/user%201/purchases?limit=100': {'items': [
                {'product_id': 'prod_native', 'status': 'owned', 'store_purchase_identifier': 'tx1'},
                {'product_id': 'prod_test', 'status': 'owned', 'store_purchase_identifier': 'tx2'},
                {'product_id': 'prod_other', 'status': 'owned', 'store_purchase_identifier': 'tx3'},
            ], 'next_page': None},
        }
        with patch('urllib.request.urlopen', self.fake_urlopen(pages)):
            purchases = face_app.revenuecat_customer_purchases('proj', 'user 1')
        self.assertEqual([p['store_purchase_identifier'] for p in purchases], ['tx1'])
        self.assertEqual(purchases[0]['revenuecat_product']['id'], 'prod_native')

    @patch.dict(os.environ, {'REVENUECAT_SECRET_API_KEY': 'sk_test', 'REVENUECAT_PRODUCT_ID': 'report'})
    def test_rest_api_failure_returns_none(self):
        def broken(request, timeout):
            raise OSError('network down')
        with patch('urllib.request.urlopen', broken):
            self.assertIsNone(face_app.revenuecat_customer_purchases('proj', 'user'))


if __name__ == '__main__':
    unittest.main()
