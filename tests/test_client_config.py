"""Client URL validation tests."""
import os
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client'))

from middlemdm import config
from middlemdm.config import validate_server_url


class ClientConfigTestCase(unittest.TestCase):
    def test_accepts_https_url(self):
        self.assertEqual(
            validate_server_url('https://mdm.example:5001/'),
            'https://mdm.example:5001',
        )

    def test_load_config_uses_https_default(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / 'config.json'
            with patch.object(config, 'CONFIG_FILE', config_file):
                loaded = config.load_config()

        self.assertEqual(loaded['server_url'], 'https://mdm.example')

    def test_load_config_rejects_remote_http_configuration(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / 'config.json'
            config_file.write_text(json.dumps({
                'server_url': 'http://10.1.1.1:5001',
                'allow_insecure_http': True,
            }), encoding='utf-8')
            with patch.object(config, 'CONFIG_FILE', config_file):
                with self.assertRaisesRegex(ValueError, 'must use HTTPS'):
                    config.load_config()

    def test_rejects_remote_http_url(self):
        with self.assertRaisesRegex(ValueError, 'must use HTTPS'):
            validate_server_url('http://10.1.1.1:5001')

    def test_loopback_http_requires_explicit_development_opt_in(self):
        with self.assertRaises(ValueError):
            validate_server_url('http://localhost:5001')

        self.assertEqual(
            validate_server_url('http://localhost:5001/', allow_insecure_http=True),
            'http://localhost:5001',
        )

        with self.assertRaisesRegex(ValueError, 'must use HTTPS'):
            validate_server_url(
                'http://10.1.1.1:5001',
                allow_insecure_http=True,
            )

    def test_rejects_credentials_and_query_values(self):
        with self.assertRaisesRegex(ValueError, 'without credentials or query values'):
            validate_server_url('https://user:password@mdm.example')
        with self.assertRaisesRegex(ValueError, 'without credentials or query values'):
            validate_server_url('https://mdm.example?token=secret')


if __name__ == '__main__':
    unittest.main()
