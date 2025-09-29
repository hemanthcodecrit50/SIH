from models.intent_classifier import classify_intent
from retrieval.rag import retrieve_static_info
from retrieval.mcp_api import get_market_weather_pest_info
from retrieval.redis_store import personalize_advisory
from models.advisory_llm import generate_advisory
from delivery.sms import send_sms
from delivery.whatsapp import send_whatsapp
from delivery.app import send_app_notification
from delivery.tts_pdf import generate_tts_pdf
from logging.action_log import log_action
from learning.continuous_learning import update_profile

def advisory_workflow(farmer_id, query):
    # 1. Classify intent
    intent = classify_intent(query)
    # 2. Retrieve static info (RAG)
    static_info = retrieve_static_info(intent)
    # 3. Retrieve external info (MCP API)
    api_info = get_market_weather_pest_info(intent, query)
    # 4. Personalize using Redis
    personalized = personalize_advisory(farmer_id, intent)
    # 5. Generate advisory using LLM
    advisory = generate_advisory(static_info, api_info, personalized)
    # 6. Deliver advisory
    send_sms(farmer_id, advisory)
    send_whatsapp(farmer_id, advisory)
    send_app_notification(farmer_id, advisory)
    generate_tts_pdf(farmer_id, advisory)
    # 7. Log action and update profile
    log_action(farmer_id, intent, advisory)
    update_profile(farmer_id, advisory)
    return advisory

# Example usage:
# result = advisory_workflow("farmer123", "What fertilizer should I use for wheat?")
# print(result)