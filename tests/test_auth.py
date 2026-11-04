"""Authentication tests."""
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server'))

from app import create_app
from app.extensions import db
from app.models.user import User, Role, DEFAULT_ROLES


class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()
        
        # Create roles
        for key, info in DEFAULT_ROLES.items():
            role = Role(name=key, display_name=info["display_name"], 
                       description=info["description"], permissions=info["permissions"])
            db.session.add(role)
        db.session.commit()
        
        admin_role = Role.query.filter_by(name='super_admin').first()
        admin = User(username='admin', password='testpass', role_id=admin_role.id)
        db.session.add(admin)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_login_page_loads(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
    
    def test_login_success(self):
        response = self.client.post('/auth/login', data={
            'username': 'admin',
            'password': 'testpass'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
