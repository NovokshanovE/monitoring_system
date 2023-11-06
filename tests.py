import unittest
from unittest.mock import patch, Mock
import motinoring
import yaml
from motinoring import DeviceMonitor  # Замените на имя вашего модуля и класса
from network_device import NetworkDevice
class TestDeviceMonitor(unittest.TestCase):
    def setUp(self):
        self.config_file = 'settings.yaml'  # Путь к тестовому файлу конфигурации

    @patch('network_device.NetworkDevice', autospec=True)
    @patch('motinoring.Logger', autospec=True)
    def test_load_config(self, MockLogger, MockNetworkDevice):
        mock_logger = MockLogger.return_value
        mock_device = MockNetworkDevice.return_value
        config_data = {
            'devices': [
                {'ip_address': '192.168.1.1', 'ping_attempts': 3},
                {'ip_address': '192.168.1.2', 'ping_attempts': 5}
            ],
            'log_file': 'test.log',
            'email': 'test@example.com'
        }

        with patch('builtins.open', unittest.mock.mock_open(read_data=yaml.dump(config_data))):
            monitor = DeviceMonitor(self.config_file)

        self.assertEqual(len(monitor.devices), 2)
        self.assertEqual(mock_device.connect.call_count, 2)
        mock_logger.assert_called_with('test.log')
    
    @patch('network_device.NetworkDevice', autospec=True)
    @patch('motinoring.Logger', autospec=True)
    @patch('motinoring.asyncio.Event', autospec=True)
    def test_start_monitoring(self, MockEvent, MockLogger, MockNetworkDevice):
        mock_logger = MockLogger.return_value
        mock_device = MockNetworkDevice.return_value
        mock_event = MockEvent.return_value

        monitor = DeviceMonitor(self.config_file)
        message_queue = queue.Queue()

        with patch.object(monitor, 'run', new_callable=unittest.mock.PropertyMock) as mock_run:
            mock_run.side_effect = [True, True, False]
            monitor.start_monitoring(message_queue)

if __name__ == '__main__':
    unittest.main()