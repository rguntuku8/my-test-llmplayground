"""
Groq API handler for fast inference models
Handles communication with Groq's API endpoints.
"""

import requests
import json
from typing import Dict, Any, List
from .base_handler import BaseHandler

class GroqHandler(BaseHandler):
    """Handler for Groq models (fast inference)"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.groq.com/openai/v1"
        self.model_mapping = {
            'grok-4-fast': 'llama-3.3-70b-versatile',  # Map to available Groq models
            'grok-4': 'llama-3.1-70b-versatile',
            'grok-2': 'llama-3.1-8b-instant',
            'grok-2-mini': 'gemma2-9b-it'
        }
    
    def generate_response(
        self, 
        model: str, 
        message: str, 
        settings: Dict[str, Any], 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate response using Groq API"""
        try:
            # Validate and normalize settings
            validated_settings = self.validate_settings(settings)
            
            # Get the actual model name for Groq API
            api_model = self.model_mapping.get(model, 'llama-3.1-70b-versatile')
            
            # Format messages
            messages = self.format_conversation_history(
                conversation_history, 
                validated_settings.get('system_prompt')
            )
            
            # Add current message
            messages.append({'role': 'user', 'content': message})
            
            # Prepare request payload
            payload = {
                'model': api_model,
                'messages': messages,
                'temperature': validated_settings.get('temperature', 0.7),
                'max_tokens': validated_settings.get('max_tokens', 2048),
                'top_p': validated_settings.get('top_p', 1.0),
                'stream': False
            }
            
            # Add optional parameters
            if 'stop' in validated_settings:
                payload['stop'] = validated_settings['stop']
            
            # Make API request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['choices'][0]['message']['content']
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                raise Exception(f"Groq API error: {error_msg}")
                        
        except requests.exceptions.Timeout:
            return self.handle_error(Exception("Request timeout"), "API call")
        except requests.exceptions.RequestException as e:
            return self.handle_error(e, "network request")
        except json.JSONDecodeError as e:
            return self.handle_error(e, "response parsing")
        except Exception as e:
            return self.handle_error(e, "generate_response")
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings specific to Groq models"""
        validated = super().validate_settings(settings)
        
        # Groq-specific max tokens limits
        max_tokens = validated.get('max_tokens', 2048)
        validated['max_tokens'] = min(max_tokens, 8192)  # Groq limit
        
        # Groq doesn't support presence_penalty, frequency_penalty, or seed
        validated.pop('presence_penalty', None)
        validated.pop('frequency_penalty', None)
        validated.pop('seed', None)
        
        return validated