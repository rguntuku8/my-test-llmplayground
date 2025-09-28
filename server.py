#!/usr/bin/env python3
"""
LLM Playground Backend Server
Handles API requests to various AI models using environment variables for secure key management.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# Import model handlers
from models.openai_handler import OpenAIHandler
from models.anthropic_handler import AnthropicHandler
from models.google_handler import GoogleHandler
from models.groq_handler import GroqHandler
from models.huggingface_handler import HuggingFaceHandler

# Load environment variables from .env file
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, '.env')
load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend communication

class LLMBackend:
    """Main backend class for handling LLM API requests"""
    
    def __init__(self):
        self.model_handlers = self._initialize_handlers()
        self.supported_models = self._get_supported_models()
        
    def _initialize_handlers(self) -> Dict[str, Any]:
        """Initialize all model handlers with their respective API keys"""
        handlers = {}
        
        # OpenAI Handler
        openai_key = os.getenv('OPENAI_API_KEY')
        if openai_key:
            handlers['openai'] = OpenAIHandler(openai_key)
            logger.info("OpenAI handler initialized")
        else:
            logger.warning("OpenAI API key not found in environment variables")
            
        # Anthropic Handler
        anthropic_key = os.getenv('ANTHROPIC_API_KEY')
        if anthropic_key:
            handlers['anthropic'] = AnthropicHandler(anthropic_key)
            logger.info("Anthropic handler initialized")
        else:
            logger.warning("Anthropic API key not found in environment variables")
            
        # Google Handler
        google_key = os.getenv('GOOGLE_API_KEY')
        if google_key:
            handlers['google'] = GoogleHandler(google_key)
            logger.info("Google handler initialized")
        else:
            logger.warning("Google API key not found in environment variables")
            
        # Groq Handler
        groq_key = os.getenv('GROQ_API_KEY')
        if groq_key:
            handlers['groq'] = GroqHandler(groq_key)
            logger.info("Groq handler initialized")
        else:
            logger.warning("Groq API key not found in environment variables")
            
        # Hugging Face Handler
        hf_token = os.getenv('HF_TOKEN')
        if hf_token:
            handlers['huggingface'] = HuggingFaceHandler(hf_token)
            logger.info("Hugging Face handler initialized")
        else:
            logger.warning("Hugging Face token not found in environment variables")
            
        return handlers
    
    def _get_supported_models(self) -> Dict[str, str]:
        """Get mapping of model names to their respective providers"""
        return {
            # OpenAI Models
            'gpt-4o': 'openai',
            'gpt-4-turbo': 'openai',
            'gpt-4': 'openai',
            'gpt-3.5-turbo': 'openai',
            
            # Anthropic Claude Models
            'claude-3-5-sonnet': 'anthropic',
            'claude-3-5-haiku': 'anthropic',
            'claude-3-opus': 'anthropic',
            'claude-3-haiku': 'anthropic',
            
            # Google Gemini Models
            'gemini-2.5-pro': 'google',
            'gemini-2.5-flash': 'google',
            'gemini-2.5-flash-lite': 'google',
            'gemini-1.0-ultra': 'google',
            'gemini-pro': 'google',
            
            # xAI Grok Models (via Groq for now)
            'grok-4-fast': 'groq',
            'grok-4': 'groq',
            'grok-2': 'groq',
            'grok-2-mini': 'groq',
        }
    
    def get_provider_for_model(self, model: str) -> Optional[str]:
        """Get the provider for a given model"""
        return self.supported_models.get(model)
    
    def validate_request(self, data: Dict[str, Any]) -> tuple[bool, str]:
        """Validate incoming request data"""
        required_fields = ['message', 'model']
        
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
        
        if not isinstance(data['message'], str) or not data['message'].strip():
            return False, "Message must be a non-empty string"
        
        if data['model'] not in self.supported_models:
            return False, f"Unsupported model: {data['model']}. Supported models: {list(self.supported_models.keys())}"
        
        return True, ""
    
    def process_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process the LLM request and return response"""
        try:
            # Validate request
            is_valid, error_msg = self.validate_request(data)
            if not is_valid:
                return {
                    'success': False,
                    'error': error_msg,
                    'error_type': 'validation_error'
                }
            
            # Get model and provider
            model = data['model']
            provider = self.get_provider_for_model(model)
            
            if provider not in self.model_handlers:
                return {
                    'success': False,
                    'error': f"Provider {provider} not available. Check API key configuration.",
                    'error_type': 'provider_unavailable'
                }
            
            # Extract parameters
            message = data['message']
            settings = data.get('settings', {})
            conversation_history = data.get('conversation_history', [])
            
            # Log settings for debugging
            logger.info(f"Processing request with settings: {settings}")
            
            # Get handler and process request
            handler = self.model_handlers[provider]
            response = handler.generate_response(
                model=model,
                message=message,
                settings=settings,
                conversation_history=conversation_history
            )
            
            return {
                'success': True,
                'response': response,
                'model': model,
                'provider': provider
            }
            
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            return {
                'success': False,
                'error': f"Internal server error: {str(e)}",
                'error_type': 'server_error'
            }

# Initialize backend
backend = LLMBackend()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'available_providers': list(backend.model_handlers.keys()),
        'supported_models': list(backend.supported_models.keys())
    })

@app.route('/api/chat', methods=['POST'])
def chat():
    """Main chat endpoint for processing LLM requests"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No JSON data provided',
                'error_type': 'invalid_request'
            }), 400
        
        result = backend.process_request(data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            status_code = 400 if result.get('error_type') == 'validation_error' else 500
            return jsonify(result), status_code
            
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': f"Server error: {str(e)}",
            'error_type': 'server_error'
        }), 500

@app.route('/api/models', methods=['GET'])
def get_models():
    """Get list of supported models and their providers"""
    return jsonify({
        'models': backend.supported_models,
        'available_providers': list(backend.model_handlers.keys())
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting LLM Playground Backend on port {port}")
    logger.info(f"Available providers: {list(backend.model_handlers.keys())}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)