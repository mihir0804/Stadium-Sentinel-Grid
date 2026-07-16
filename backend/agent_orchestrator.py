import os
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Configure strict system logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Universal Safe System Configuration for Emergency/Operational Environments
SAFE_CONFIG: List[types.SafetySetting] = [
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
]

def _get_gemini_client() -> genai.Client:
    """
    Initializes and returns the Google GenAI Client securely via environment variables.
    
    Returns:
        genai.Client: Securely configured GenAI client instance.
    """
    api_key: Optional[str] = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.error("Critical Failure: GOOGLE_API_KEY missing from environment context.")
    return genai.Client(api_key=api_key)

def _get_model_id(model_env_var: str = "GEMINI_MODEL_ID", default_model: str = "gemini-1.5-pro") -> str:
    """
    Resolves the targeted Gemini Model ID from the active environment.
    
    Args:
        model_env_var (str): Environment variable key for the model ID.
        default_model (str): Hardcoded fallback model ID.
        
    Returns:
        str: Validated Model ID string.
    """
    return os.getenv(model_env_var, default_model)

def operations_agent(query: str, status_telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Stadium Operations Center (SOC) Intelligence Node for FIFA World Cup 2026.
    Processes live crowd metrics, transit dynamics, and architectural incident logs.
    
    Args:
        query (str): Active incident report or staff operational query.
        status_telemetry (Optional[Dict[str, Any]]): Structural stadium telemetry payload.
        
    Returns:
        Dict[str, Any]: Strictly formatted JSON response tracking risk parameters.
    """
    telemetry_context: str = ""
    if status_telemetry:
        telemetry_context = f"\nReal-time Telemetry Data:\n{json.dumps(status_telemetry, indent=2)}\n"

    system_instruction: str = (
        "You are the Stadium Operations Center (SOC) intelligence hub for the FIFA 2026 World Cup. "
        "Your task is to analyze operational queries, crowd bottlenecks, transit feeds, and gate updates. "
        "You MUST return your response as a raw JSON object containing exactly these three keys:\n"
        "1. 'risk_level': Must be exactly 'Low', 'Medium', or 'High'.\n"
        "2. 'affected_zones': A list of strings representing the stadium zones affected.\n"
        "3. 'action_protocol': A string detailing the mitigation protocol."
    )
    
    prompt: str = f"{system_instruction}\n{telemetry_context}\nStaff Query: {query}"
    
    try:
        client: genai.Client = _get_gemini_client()
        model_id: str = _get_model_id()
        
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                safety_settings=SAFE_CONFIG,
                temperature=0.2
            )
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Operations Node Execution Exception: {str(e)}")
        return {
            "risk_level": "Medium",
            "affected_zones": ["Unknown / Global System Context"],
            "action_protocol": "Fallback Safety Protocol: Deploy nearest localized ground units for visual validation."
        }

def accessibility_assistant(query: str, language: str) -> str:
    """
    Inclusive Accessibility Router for mobility, visually, or auditorily impaired fans.
    
    Args:
        query (str): Navigational or operational assistance query.
        language (str): ISO target language for response localization.
        
    Returns:
        str: Dignified, clear routing guidance matching stadium accessibility specifications.
    """
    system_instruction: str = (
        f"You are an inclusive stadium accessibility assistant for the FIFA 2026 World Cup. "
        f"Provide safe, clear, and dignified routing and assistance for fans with mobility, visual, or auditory impairments. "
        f"Your response MUST be exclusively in the following language: {language}. "
        f"Base your guidance on standard accessible stadium infrastructure (e.g., elevators, sensory rooms, accessible ramps and restrooms). "
        f"Be concise, reassuring, and extremely clear with directions."
    )
    
    prompt: str = f"{system_instruction}\n\nFan Request: {query}"
    
    try:
        client: genai.Client = _get_gemini_client()
        model_id: str = _get_model_id()
        
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                safety_settings=SAFE_CONFIG,
                temperature=0.3
            )
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Accessibility Node Execution Exception: {str(e)}")
        return f"System Connectivity Interruption. Please report to the closest physical Information Gateway."

def route_stadium_query(user_query: str, user_role: str, telemetry: Optional[Dict[str, Any]] = None, language: str = "English") -> Any:
    """
    Orchestration Engine routing incoming architectural data streams to respective processing nodes.
    
    Args:
        user_query (str): Incoming unstructured query string.
        user_role (str): Operational access tier ('staff' or 'fan').
        telemetry (Optional[Dict[str, Any]]): Contextual telemetry data matrix.
        language (str): Desired output language localization token.
        
    Returns:
        Any: Structured JSON payload for operators, or localized string response for fans.
    """
    normalized_role: str = user_role.lower().strip()
    logger.info(f"Routing transaction context for role: {normalized_role} | target_locale: {language}")
    
    if normalized_role == "staff":
        return operations_agent(query=user_query, status_telemetry=telemetry)
        
    elif normalized_role == "fan":
        accessibility_keywords: List[str] = [
            "wheelchair", "blind", "deaf", "ramp", "elevator", "sensory", 
            "impaired", "guide dog", "disabled", "accessible", "assistance", "mobility"
        ]
        
        is_accessibility_intent: bool = any(k in user_query.lower() for k in accessibility_keywords)
        
        if is_accessibility_intent:
            return accessibility_assistant(query=user_query, language=language)
        else:
            try:
                client: genai.Client = _get_gemini_client()
                model_id: str = _get_model_id()
                prompt: str = f"You are a helpful FIFA 2026 stadium assistant. Respond accurately in {language}. Fan asks: {user_query}"
                
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        safety_settings=SAFE_CONFIG,
                        temperature=0.4
                    )
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"Global Fan Node Processing Exception: {str(e)}")
                return "Transaction processing error. Please interface with physical tournament personnel."
    
    else:
        logger.warning(f"Malformed configuration role rejected: {user_role}")
        return {"error": "Invalid user_role context token executed."}
