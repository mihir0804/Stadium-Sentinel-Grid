import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Import the new GenAI SDK
from google import genai
from google.genai import types

# Load environment variables from .env file
load_dotenv()

# Initialize logging for the orchestrator
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def _get_gemini_client() -> genai.Client:
    """
    Initializes and returns the new Gemini client securely using environment variables.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_API_KEY not found in environment variables. Ensure it is set before making API calls.")
    return genai.Client(api_key=api_key)

def _get_model_id(model_env_var: str = "GEMINI_MODEL_ID", default_model: str = "gemini-1.5-pro") -> str:
    return os.getenv(model_env_var, default_model)

# --- Universal Safety Settings for Security/Emergency App ---
safe_config = [
    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE"),
]

def operations_agent(query: str, status_telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Acts as an automated Stadium Operations Center (SOC) intelligence hub for FIFA 2026.
    Analyzes crowd bottlenecks, transit feeds, and gate updates.
    """
    telemetry_context = ""
    if status_telemetry:
        telemetry_context = f"\nReal-time Telemetry Data:\n{json.dumps(status_telemetry, indent=2)}\n"

    system_instruction = (
        "You are the Stadium Operations Center (SOC) intelligence hub for the FIFA 2026 World Cup. "
        "Your task is to analyze operational queries, crowd bottlenecks, transit feeds, and gate updates. "
        "You MUST return your response as a raw JSON object containing exactly these three keys:\n"
        "1. 'risk_level': Must be exactly 'Low', 'Medium', or 'High'.\n"
        "2. 'affected_zones': A list of strings representing the stadium zones affected.\n"
        "3. 'action_protocol': A string detailing the mitigation protocol."
    )
    
    prompt = f"{system_instruction}\n{telemetry_context}\nStaff Query: {query}"
    
    try:
        client = _get_gemini_client()
        model_id = _get_model_id()
        
        # Requesting structured JSON response and disabling safety blocks
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                safety_settings=safe_config,
                temperature=0.2
            )
        )
        return json.loads(response.text)
    except Exception as e:
        logger.error(f"Operations Agent Execution Error: {str(e)}")
        # Graceful degradation: Return standard fallback protocol
        return {
            "risk_level": "Medium",
            "affected_zones": ["Unknown / All"],
            "action_protocol": "Standard Fallback Protocol Initiated: Dispatch ground personnel to visually assess the situation and maintain direct communication via radio."
        }

def accessibility_assistant(query: str, language: str) -> str:
    """
    An inclusive RAG assistant optimized to route mobility, visually, or auditorily 
    impaired fans safely through the stadium infrastructure.
    """
    system_instruction = (
        f"You are an inclusive stadium accessibility assistant for the FIFA 2026 World Cup. "
        f"Provide safe, clear, and dignified routing and assistance for fans with mobility, visual, or auditory impairments. "
        f"Your response MUST be exclusively in the following language: {language}. "
        f"Base your guidance on standard accessible stadium infrastructure (e.g., elevators, sensory rooms, accessible ramps and restrooms). "
        f"Be concise, reassuring, and extremely clear with directions."
    )
    
    prompt = f"{system_instruction}\n\nFan Request: {query}"
    
    try:
        client = _get_gemini_client()
        model_id = _get_model_id()
        
        # Disabling safety blocks so wheelchair/medical words don't get rejected
        response = client.models.generate_content(
            model=model_id,
            contents=prompt,
            config=types.GenerateContentConfig(
                safety_settings=safe_config,
                temperature=0.3
            )
        )
        return response.text.strip()
    except Exception as e:
        logger.error(f"Accessibility Assistant Execution Error: {str(e)}")
        # Graceful degradation with fallback instructions
        return (
            f"Fallback Assistance [{language}]: We are experiencing temporary connectivity issues. "
            f"Please remain where you are safely, and locate the nearest Information Desk or a staff member in a high-visibility jacket for immediate assistance."
        )

def route_stadium_query(user_query: str, user_role: str, telemetry: Optional[Dict[str, Any]] = None, language: str = "English") -> Any:
    """
    Dynamically routes a stadium query to the appropriate agent node based on the user's role and intent.
    """
    normalized_role = user_role.lower().strip()
    
    logger.info(f"Routing query for role: {normalized_role} | language: {language}")
    
    # 1. Staff Routing
    if normalized_role == "staff":
        logger.info("Triggering operations_agent.")
        return operations_agent(query=user_query, status_telemetry=telemetry)
        
    # 2. Fan Routing
    elif normalized_role == "fan":
        accessibility_keywords = [
            "wheelchair", "blind", "deaf", "ramp", "elevator", "sensory", 
            "impaired", "guide dog", "disabled", "accessible", "assistance", "mobility"
        ]
        
        is_accessibility_intent = any(keyword in user_query.lower() for keyword in accessibility_keywords)
        
        if is_accessibility_intent:
            logger.info("Accessibility intent detected. Triggering accessibility_assistant.")
            return accessibility_assistant(query=user_query, language=language)
        else:
            logger.info("Standard fan query detected. Triggering general response.")
            try:
                client = _get_gemini_client()
                model_id = _get_model_id()
                
                prompt = (
                    f"You are a helpful FIFA 2026 stadium assistant. Respond accurately in {language}. "
                    f"Fan asks: {user_query}"
                )
                response = client.models.generate_content(
                    model=model_id,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        safety_settings=safe_config,
                        temperature=0.4
                    )
                )
                return response.text.strip()
            except Exception as e:
                logger.error(f"General Fan Agent Error: {str(e)}")
                return "Error: Unable to process request. Please contact stadium staff."
    
    # 3. Invalid Role
    else:
        logger.warning(f"Invalid user_role provided: {user_role}")
        return {"error": "Invalid user_role provided. Must be 'staff' or 'fan'."}
