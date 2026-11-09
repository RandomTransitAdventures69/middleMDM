"""Client platform compatibility tests."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'client'))

from middlemdm import config
from middlemdm.agent import Agent
from middlemdm.collectors import system


class ClientPlatformTestCase(unittest.TestCase):
    def test_config_directories_follow_platform_conventions(self):
        with patch.object(config.sys, 'platform', 'darwin'), \
             patch.object(Path, 'home', return_value=Path('/Users/tester')):
            self.assertEqual(
                config.get_config_dir(),
                Path('/Users/tester/Library/Application Support/middleMDM'),
            )

        with patch.object(config.sys, 'platform', 'linux'), \
             patch.dict(os.environ, {'XDG_CONFIG_HOME': '/tmp/test-config'}):
            self.assertEqual(
                config.get_config_dir(),
                Path('/tmp/test-config/middlemdm'),
            )

    def test_agent_uses_platform_specific_stable_device_id(self):
        with tempfile.TemporaryDirectory() as temp_dir, \
             patch.object(config, 'load_config', return_value={}), \
             patch.object(config, 'save_config'), \
             patch('middlemdm.agent.system.get_machine_id', return_value='stable-machine-id'), \
             patch('middlemdm.agent.platform.system', return_value='Darwin'):
            agent = Agent()
            first_id = agent.get_device_id()
            second_id = agent.get_device_id()

        self.assertTrue(first_id.startswith('MAC-'))
        self.assertEqual(first_id, second_id)

    def test_storage_marks_posix_root_as_system_disk(self):
        partition = type(
            'Partition',
            (),
            {'device': '/dev/root', 'mountpoint': '/', 'fstype': 'ext4'},
        )()
        usage = type('Usage', (), {'total': 100, 'free': 50})()
        with patch('middlemdm.collectors.system.platform.system', return_value='Linux'), \
             patch('middlemdm.collectors.system.psutil.disk_partitions', return_value=[partition]), \
             patch('middlemdm.collectors.system.psutil.disk_usage', return_value=usage):
            storage = system.get_storage()

        self.assertEqual(len(storage), 1)
        self.assertTrue(storage[0]['is_system'])

    def test_macos_hardware_info_reads_system_profiler_json(self):
        result = type(
            'Result',
            (),
            {'stdout': json.dumps({'SPHardwareDataType': [{'machine_model': 'Mac15,7'}]})},
        )()
        system._mac_hardware_info.cache_clear()
        self.addCleanup(system._mac_hardware_info.cache_clear)
        with patch('middlemdm.collectors.system.subprocess.run', return_value=result):
            self.assertEqual(system._mac_hardware_info(), {'machine_model': 'Mac15,7'})


if __name__ == '__main__':
    unittest.main()
