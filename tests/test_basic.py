"""Basic tests for middleMDM."""
import unittest
import os
import sys

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server'))

from app import create_app
from app.extensions import db
from app.models.user import User, Role
from app.models.device import Device


class BasicTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_app_exists(self):
        self.assertFalse(self.app is None)
    
    def test_app_is_testing(self):
        self.assertTrue(self.app.config['TESTING'])

    def test_root_redirects_to_dashboard(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 302)
        self.assertIn('/dashboard/', response.headers['Location'])

    def test_login_page_loads_stylesheet(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn('/static/css/style.css', response.get_data(as_text=True))
        stylesheet = self.client.get('/static/css/style.css')
        self.assertEqual(stylesheet.status_code, 200)

    def test_production_enforces_csrf_but_api_is_exempt(self):
        production_app = create_app('production')
        production_client = production_app.test_client()

        login_response = production_client.post('/auth/login', data={})
        api_response = production_client.post('/api/v1/heartbeat', json={})

        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(api_response.status_code, 401)


if __name__ == '__main__':
    unittest.main()
