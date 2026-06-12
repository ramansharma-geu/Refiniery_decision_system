from flask import Blueprint, render_template, request, jsonify, current_app
from services import db_service
from services.slm_service import SLMService
from chatbot.hybrid_retriever import get_hybrid_chatbot_response

chatbot_bp = Blueprint('chatbot', __name__)

def get_slm_service():
    """
    Creates an instance of SLMService using Flask app configurations.
    """
    return SLMService(
        provider=current_app.config['SLM_PROVIDER'],
        ollama_url=current_app.config['OLLAMA_URL'],
        ollama_model=current_app.config['OLLAMA_MODEL'],
        hf_model_path=current_app.config['HF_MODEL_PATH']
    )

@chatbot_bp.route('/chatbot')
def chat_interface():
    logs = db_service.get_chatbot_logs(limit=25)
    # Reverse to make chronological for standard chat layout
    logs.reverse()
    return render_template(
        'chatbot.html',
        logs=[l.to_dict() for l in logs],
        active_page='chatbot'
    )

@chatbot_bp.route('/chatbot/query', methods=['POST'])
def chat_query():
    data = request.get_json() or {}
    query_text = data.get('query', '').strip()
    
    if not query_text:
        return jsonify({"error": "Empty query query parameter."}), 400
        
    try:
        slm = get_slm_service()
        response_data = get_hybrid_chatbot_response(query_text, slm)
        return jsonify(response_data)
    except Exception as e:
        print(f"Error handling chatbot query: {e}")
        return jsonify({
            "response": f"Internal chatbot service error: {e}. Please contact system engineering.",
            "db_data": [],
            "llm_called": False
        }), 500
