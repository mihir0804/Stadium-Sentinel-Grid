import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from google.api_core.exceptions import GoogleAPIError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize logging for the orchestrator
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def _get_gemini_model(model_env_var: str = "GEMINI_MODEL_ID", default_model: str = "gemini-1.5-pro") -> genai.GenerativeModel:
    """
    Initializes and returns the Gemini model securely using environment variables.
    
    Args:
        model_env_var (str): The environment variable containing the model ID.
        default_model (str): The fallback model ID if the environment variable is not set.
        
    Returns:
        genai.GenerativeModel: The initialized GenerativeModel instance.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if api_key:
        genai.configure(api_key=api_key)
    else:
        logger.warning("GOOGLE_API_KEY not found in environment variables. Ensure it is set before making API calls.")

    model_id = os.getenv(model_env_var, default_model)
    return genai.GenerativeModel(model_id)

def operations_agent(query: str, status_telemetry: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Acts as an automated Stadium Operations Center (SOC) intelligence hub for FIFA 2026.
    Analyzes crowd bottlenecks, transit feeds, and gate updates.
    
    Args:
        query (str): The operational query or report from the staff.
        status_telemetry (Optional[Dict[str, Any]]): Real-time telemetry data (e.g., gate density, transit status).
        
    Returns:
        Dict[str, Any]: A structured JSON response containing:
            - 'risk_level' (str): 'Low', 'Medium', or 'High'
            - 'affected_zones' (List[str]): List of zones affected by the issue
            - 'action_protocol' (str): Step-by-step mitigation or action protocol
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
        model = _get_gemini_model()
        # Requesting structured JSON response from Gemini
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                response_mime_type="application/json"
            )
        )
        return json.loads(response.text)
    except (GoogleAPIError, json.JSONDecodeError, Exception) as e:
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
    
    Args:
        query (str): The assistance request from the fan.
        language (str): The language in which the response should be provided.
        
    Returns:
        str: Tailored accessibility guidance in the requested language.
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
        model = _get_gemini_model()
        response = model.generate_content(prompt)
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
    
    Args:
        user_query (str): The input query from the user.
        user_role (str): The role of the user (must be 'staff' or 'fan').
        telemetry (Optional[Dict[str, Any]]): Optional telemetry data, used primarily for staff queries.
        language (str): The preferred language of the user. Defaults to "English".
        
    Returns:
        Any: The payload from the triggered agent. 
             - Dict for Operations Agent.
             - String for Accessibility Assistant.
             - Dict/String for errors or standard routing.
    """
    normalized_role = user_role.lower().strip()
    
    logger.info(f"Routing query for role: {normalized_role} | language: {language}")
    
    # 1. Staff Routing
    if normalized_role == "staff":
        logger.info("Triggering operations_agent.")
        return operations_agent(query=user_query, status_telemetry=telemetry)
        
    # 2. Fan Routing
    elif normalized_role == "fan":
        # Simple intent parsing heuristic (could be upgraded to an LLM router for complex cases)
        accessibility_keywords = [
            "wheelchair", "blind", "deaf", "ramp", "elevator", "sensory", 
            "impaired", "guide dog", "disabled", "accessible", "assistance", "mobility"
        ]
        
        is_accessibility_intent = any(keyword in user_query.lower() for keyword in accessibility_keywords)
        
        if is_accessibility_intent:
            logger.info("Accessibility intent detected. Triggering accessibility_assistant.")
            return accessibility_assistant(query=user_query, language=language)
        else:
            # Fallback for standard fan queries
            logger.info("Standard fan query detected. Triggering general response.")
            try:
                model = _get_gemini_model()
                prompt = (
                    f"You are a helpful FIFA 2026 stadium assistant. Respond accurately in {language}. "
                    f"Fan asks: {user_query}"
                )
                response = model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                logger.error(f"General Fan Agent Error: {str(e)}")
                return "Error: Unable to process request. Please contact stadium staff."
    
    # 3. Invalid Role
    else:
        logger.warning(f"Invalid user_role provided: {user_role}")
        return {"error": "Invalid user_role provided. Must be 'staff' or 'fan'."}
