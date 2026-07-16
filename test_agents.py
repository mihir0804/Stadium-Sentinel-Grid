import unittest
from unittest.mock import MagicMock, patch
from backend.agent_orchestrator import route_stadium_query, operations_agent

class TestStadiumSentinel(unittest.TestCase):
    def setUp(self):
        self.sample_telemetry = {"gate_alpha_density": "85%", "active_incidents": 1}

    def test_staff_routing_execution(self):
        """Ensure staff queries route to the operations agent correctly."""
        with patch('backend.agent_orchestrator.operations_agent') as mock_ops:
            mock_ops.return_value = {"risk_level": "High", "affected_zones": ["Gate C"]}
            response = route_stadium_query("Crowd surge at Gate C", "staff", self.sample_telemetry)
            self.assertEqual(response["risk_level"], "High")

    def test_fan_accessibility_detection(self):
        """Validate that mobility keywords correctly trigger accessibility logic."""
        with patch('backend.agent_orchestrator.accessibility_assistant') as mock_access:
            mock_access.return_value = "Safe alternative route mapped."
            response = route_stadium_query("Where is the wheelchair ramp?", "fan", language="English")
            self.assertEqual(response, "Safe alternative route mapped.")

if __name__ == '__main__':
    unittest.main()
