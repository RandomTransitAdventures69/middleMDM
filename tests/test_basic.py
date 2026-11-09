"""Basic tests for middleMDM."""
import unittest
import os
import sys
from unittest.mock import patch

# Add server to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server'))

from app import create_app
from config import ProductionConfig
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
        html = response.get_data(as_text=True)
        self.assertIn('/static/css/style.css', html)
        self.assertIn('class="login-box"', html)
        stylesheet = self.client.get('/static/css/style.css')
        self.assertEqual(stylesheet.status_code, 200)
        css = stylesheet.get_data(as_text=True)
        self.assertIn('.login-box', css)
        self.assertIn('.sidebar', css)
        self.assertIn('.summary-panels', css)
        for reference_layout_rule in (
            'height: 48px',
            'width: 220px',
            'max-width: 380px',
        ):
            self.assertIn(reference_layout_rule, css)

    def test_production_enforces_csrf_but_api_is_exempt(self):
        with patch.object(
            ProductionConfig,
            'SECRET_KEY',
            'server-secret-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        ), patch.object(
            ProductionConfig,
            'ENROLLMENT_SECRET',
            'enrollment-secret-abcdefghijklmnopqrstuvwxyz-0123456789',
        ):
            production_app = create_app()
        production_client = production_app.test_client()

        login_response = production_client.post('/auth/login', data={})
        api_response = production_client.post('/api/v1/heartbeat', json={})

        self.assertEqual(login_response.status_code, 400)
        self.assertEqual(api_response.status_code, 401)

    def test_production_rejects_missing_secrets(self):
        with patch.object(ProductionConfig, 'SECRET_KEY', None):
            with self.assertRaisesRegex(RuntimeError, 'SECRET_KEY'):
                create_app('production')

    def test_production_rejects_low_diversity_secrets(self):
        with patch.object(ProductionConfig, 'SECRET_KEY', 's' * 48):
            with self.assertRaisesRegex(RuntimeError, 'SECRET_KEY'):
                create_app('production')

    def test_production_rejects_reused_secrets(self):
        secret = 'server-secret-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        with patch.object(ProductionConfig, 'SECRET_KEY', secret), \
             patch.object(ProductionConfig, 'ENROLLMENT_SECRET', secret):
            with self.assertRaisesRegex(RuntimeError, 'must be different'):
                create_app('production')

    def test_production_rejects_known_enrollment_secret(self):
        with patch.object(
            ProductionConfig,
            'SECRET_KEY',
            'server-secret-0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ',
        ), \
             patch.object(
                 ProductionConfig,
                 'ENROLLMENT_SECRET',
                 'dev-enrollment-secret-change-me',
             ):
            with self.assertRaisesRegex(RuntimeError, 'ENROLLMENT_SECRET'):
                create_app('production')

    def test_init_db_prompts_for_unique_admin_password(self):
        result = self.app.test_cli_runner().invoke(
            args=['init-db'],
            input='a-unique-password-with-12-chars\n'
                  'a-unique-password-with-12-chars\n',
        )

        self.assertEqual(result.exit_code, 0, result.output)
        admin = User.query.filter_by(username='admin').one()
        self.assertTrue(admin.check_password('a-unique-password-with-12-chars'))

    def test_init_db_accepts_password_from_stdin_for_setup_apps(self):
        password = 'another-unique-password-123'
        result = self.app.test_cli_runner().invoke(
            args=['init-db', '--admin-password-stdin'],
            input=f'{password}\n{password}\n',
        )

        self.assertEqual(result.exit_code, 0, result.output)
        admin = User.query.filter_by(username='admin').one()
        self.assertTrue(admin.check_password(password))

    def test_dashboard_contains_reference_layout_sections(self):
        role = Role(
            name='dashboard_test',
            display_name='Dashboard Test',
            permissions=['system:read'],
        )
        db.session.add(role)
        db.session.commit()
        db.session.add(User(username='layout-user', password='long-test-password', role_id=role.id))
        db.session.commit()
        self.client.post('/auth/login', data={
            'username': 'layout-user',
            'password': 'long-test-password',
        })

        response = self.client.get('/dashboard/')
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn('class="sidebar"', html)
        self.assertIn('class="summary-panels"', html)
        self.assertIn('Recent devices', html)
        self.assertIn('Recent activity', html)

    def test_device_detail_is_rendered_with_stylesheet(self):
        role = Role(
            name='device_view_test',
            display_name='Device View Test',
            permissions=['devices:read'],
        )
        db.session.add(role)
        db.session.commit()
        db.session.add(User(username='device-view-user', password='long-test-password', role_id=role.id))
        device = Device(device_id='device-template-test', hostname='test-workstation')
        db.session.add(device)
        db.session.commit()
        self.client.post('/auth/login', data={
            'username': 'device-view-user',
            'password': 'long-test-password',
        })

        response = self.client.get(f'/dashboard/devices/{device.id}')
        html = response.get_data(as_text=True)
        stylesheet = self.client.get('/static/css/style.css')

        self.assertEqual(response.status_code, 200)
        self.assertIn('href="/static/css/style.css"', html)
        self.assertIn('class="sidebar"', html)
        self.assertIn('test-workstation', html)
        self.assertNotIn('{% extends', html)
        self.assertNotIn('{{ device.', html)
        self.assertEqual(stylesheet.status_code, 200)


if __name__ == '__main__':
    unittest.main()
