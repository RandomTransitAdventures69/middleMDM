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


if __name__ == '__main__':
    unittest.main()
