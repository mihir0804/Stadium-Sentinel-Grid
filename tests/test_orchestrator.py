import os
import sys
import json
import pytest
from unittest.mock import patch, MagicMock

# Dynamically inject the root project path into sys.path to allow absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from backend.agent_orchestrator import (
    _get_gemini_model,
    operations_agent,
    accessibility_assistant,
    route_stadium_query
)

# ==============================================================================
# 1. Environment Variable Integrity Test
# ==============================================================================
@patch.dict(os.environ, {"GOOGLE_API_KEY": "fake_api_key_123", "GEMINI_MODEL_ID": "gemini-test-model-pro"})
@patch('backend.agent_orchestrator.genai.configure')
def test_environment_initialization(mock_configure):
    """
    Validates that the orchestrator securely initializes model configurations
    by pulling from OS environment variables instead of hardcoded strings.
    """
    # Execute initialization
    model = _get_gemini_model()
    
    # Assert the SDK was configured properly using the environment API key
    mock_configure.assert_called_once_with(api_key="fake_api_key_123")
    
    # Assert the returned generative model is leveraging the exact model specified in the env
    assert model.model_name == "models/gemini-test-model-pro", "Model ID failed to parse from env"

# ==============================================================================
# 2. Structured Schema Output Test
# ==============================================================================
@patch('backend.agent_orchestrator._get_gemini_model')
def test_operations_structured_schema_output(mock_get_model):
    """
    Verifies that invoking the operations_agent natively maps to a strict dictionary
    matching the schema requirements, properly simulating successful LLM serialization.
    """
    # Setup mock LLM model and API response payload
    mock_model = MagicMock()
    mock_response = MagicMock()
    
    valid_json_payload = json.dumps({
        "risk_level": "High",
        "affected_zones": ["Gate Alpha", "Transit Hub 1"],
        "action_protocol": "Dispatch immediate medical and crowd control units."
    })
    
    mock_response.text = valid_json_payload
    mock_model.generate_content.return_value = mock_response
    mock_get_model.return_value = mock_model
    
    # Inject mock telemetry
    mock_telemetry = {"gate_alpha_density": "85%", "transit_line_status": "delayed"}
    
    # Execute execution
    result = operations_agent(query="Overcrowding at Gate Alpha", status_telemetry=mock_telemetry)
    
    # Strict schema and data type boundaries validation
    assert isinstance(result, dict), "Payload must be a dictionary"
    assert "risk_level" in result
    assert "affected_zones" in result
    assert "action_protocol" in result
    assert result["risk_level"] == "High"
    assert isinstance(result["affected_zones"], list)
    assert len(result["affected_zones"]) == 2

# ==============================================================================
# 3. Multi-Language Isolation Test
# ==============================================================================
@patch('backend.agent_orchestrator._get_gemini_model')
def test_accessibility_multi_language_isolation(mock_get_model):
    """
    Validates that the accessibility_assistant properly receives the language payload 
    and constructs a localized prompt request for the GenerativeModel.
    """
    mock_model = MagicMock()
    mock_response = MagicMock()
    
    mock_response.text = "Por favor, diríjase al ascensor accesible más cercano en la Zona Norte."
    mock_model.generate_content.return_value = mock_response
    mock_get_model.return_value = mock_model
    
    # Execute assistant mapping to Spanish locale
    result = accessibility_assistant(query="Where is the wheelchair ramp?", language="Spanish")
    
    # Assert basic string structure boundary
    assert isinstance(result, str)
    assert len(result) > 0
    assert "ascensor" in result

    # Intercept prompt payload to ensure the language parameter successfully mapped to the prompt string
    args, kwargs = mock_model.generate_content.call_args
    prompt_sent = args[0]
    
    assert "Spanish" in prompt_sent, "Language contextualizer failed to route to prompt"
    assert "wheelchair ramp" in prompt_sent, "Fan query failed to route to prompt"

# ==============================================================================
# 4. Edge Case Fault Tolerance 
# ==============================================================================
def test_router_fault_tolerance_invalid_roles():
    """
    Validates that the primary route_stadium_query fallback handler cleanly intercepts
    unauthorized or invalid roles, returning a standard dictionary payload rather than crashing.
    """
    result = route_stadium_query(user_query="Status update", user_role="unauthorized_entity")
    
    # Ensure system degradation produces the specific error schema payload
    assert isinstance(result, dict)
    assert "error" in result
    assert "Invalid user_role" in result["error"]

@patch('backend.agent_orchestrator._get_gemini_model')
def test_agent_graceful_degradation_api_crash(mock_get_model):
    """
    Tests resilient fallbacks against API connection drops. If Google API fails (simulated via Exception),
    operations_agent and accessibility_assistant must catch it and return fallback instructions cleanly.
    """
    mock_model = MagicMock()
    # Force the API execution to crash natively simulating a connectivity drop
    mock_model.generate_content.side_effect = Exception("503 Service Unavailable API Dropout")
    mock_get_model.return_value = mock_model
    
    # Test Operations Fallback
    operations_result = operations_agent(query="CRITICAL: Gateway offline", status_telemetry=None)
    
    assert isinstance(operations_result, dict)
    assert operations_result["risk_level"] == "Medium"
    assert "Standard Fallback Protocol Initiated" in operations_result["action_protocol"]
    
    # Test Accessibility Fallback
    accessibility_result = accessibility_assistant(query="Need guide dog assistance", language="French")
    
    assert isinstance(accessibility_result, str)
    assert "Fallback Assistance [French]" in accessibility_result
