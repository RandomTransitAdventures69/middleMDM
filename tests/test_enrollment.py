"""Device enrollment tests."""
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server'))

from app import create_app
from app.extensions import db


class EnrollmentTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        self.enrollment_secret = self.app.config['ENROLLMENT_SECRET']
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_enroll_device(self):
        response = self.client.post('/api/v1/enroll', json={
            'enrollment_secret': self.enrollment_secret,
            'device_id': 'TEST-DEVICE-001',
            'hostname': 'test-pc',
            'os_name': 'Windows',
            'os_version': '10.0'
        })
        self.assertIn(response.status_code, [200, 201])
        data = response.get_json()
        self.assertIn('api_token', data)


if __name__ == '__main__':
    unittest.main()
