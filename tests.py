import unittest
from unittest.mock import Mock, patch, MagicMock
from motinoring import DeviceMonitor, NetworkDevice

class TestDeviceMonitor(unittest.TestCase):
    def setUp(self):
        config_file = "settings.yaml"
        self.monitor = DeviceMonitor(config_file)

    def test_pause_monitoring(self):
        self.monitor.pause_monitoring()
        self.assertTrue(self.monitor.paused)

    def test_resume_monitoring(self):
        self.monitor.paused = True  # Установим состояние на паузе для теста
        self.monitor.resume_monitoring()
        self.assertFalse(self.monitor.paused)

    @patch('asyncio.Event.set')
    def test_resume_monitoring_with_event_set(self, mock_event_set):
        self.monitor.paused = True  # Установим состояние на паузе для теста
        self.monitor.resume_monitoring()
        self.assertFalse(self.monitor.paused)
        mock_event_set.assert_called()

    




    


    

if __name__ == '__main__':
    unittest.main()