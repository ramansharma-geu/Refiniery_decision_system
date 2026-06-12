import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'refinery-decision-intelligence-secret-key-9988')
    
    # SQLite Database Configuration
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 
        f"sqlite:///{os.path.join(BASE_DIR, 'refinery.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # SLM Configurations (mock, ollama, huggingface)
    SLM_PROVIDER = os.environ.get('SLM_PROVIDER', 'mock')
    OLLAMA_URL = os.environ.get('OLLAMA_URL', 'http://localhost:11434/api/generate')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'qwen2.5:1.5b')
    HF_MODEL_PATH = os.environ.get('HF_MODEL_PATH', 'TinyLlama/TinyLlama-1.1B-Chat-v1.0')
