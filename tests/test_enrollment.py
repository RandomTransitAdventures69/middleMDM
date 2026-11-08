"""Device enrollment tests."""
import unittest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'server'))

from app import create_app
from app.extensions import db
from app.models.inventory import NetworkInterface


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

    def test_device_token_header_authenticates_get_request(self):
        response = self.client.post('/api/v1/enroll', json={
            'enrollment_secret': self.enrollment_secret,
            'device_id': 'TEST-DEVICE-002',
            'hostname': 'test-pc',
        })
        token = response.get_json()['api_token']

        device_info = self.client.get(
            '/api/v1/devices/info',
            headers={'X-Device-Token': token},
        )

        self.assertEqual(device_info.status_code, 200)
        self.assertEqual(device_info.get_json()['device_id'], 'TEST-DEVICE-002')

    def test_network_report_persists_interfaces(self):
        response = self.client.post('/api/v1/enroll', json={
            'enrollment_secret': self.enrollment_secret,
            'device_id': 'TEST-DEVICE-003',
            'hostname': 'network-test',
        })
        token = response.get_json()['api_token']

        network_response = self.client.post(
            '/api/v1/network',
            headers={'Authorization': f'Bearer {token}'},
            json={'network_interfaces': [{
                'name': 'Ethernet',
                'mac_address': '00:11:22:33:44:55',
                'ip_addresses': ['192.0.2.10'],
                'is_active': True,
            }]},
        )

        self.assertEqual(network_response.status_code, 200)
        interface = NetworkInterface.query.one()
        self.assertEqual(interface.name, 'Ethernet')
        self.assertEqual(interface.get_ip_addresses(), ['192.0.2.10'])

    def test_inventory_rejects_invalid_collection_shapes(self):
        response = self.client.post('/api/v1/enroll', json={
            'enrollment_secret': self.enrollment_secret,
            'device_id': 'TEST-DEVICE-004',
            'hostname': 'inventory-test',
        })
        token = response.get_json()['api_token']

        inventory_response = self.client.post(
            '/api/v1/inventory',
            headers={'Authorization': f'Bearer {token}'},
            json={'network_interfaces': 'not-a-list'},
        )

        self.assertEqual(inventory_response.status_code, 400)


if __name__ == '__main__':
    unittest.main()
