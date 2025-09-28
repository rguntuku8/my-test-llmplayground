"""
OpenAI API handler for GPT models
Handles communication with OpenAI's API endpoints.
"""

import requests
import json
from typing import Dict, Any, List
from .base_handler import BaseHandler

class OpenAIHandler(BaseHandler):
    """Handler for OpenAI GPT models"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.openai.com/v1"
        self.model_mapping = {
            'gpt-4o': 'gpt-4o',
            'gpt-4-turbo': 'gpt-4-turbo-preview',
            'gpt-4': 'gpt-4',
            'gpt-3.5-turbo': 'gpt-3.5-turbo'
        }
    
    def generate_response(
        self, 
        model: str, 
        message: str, 
        settings: Dict[str, Any], 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate response using OpenAI API"""
        try:
            # Validate and normalize settings
            validated_settings = self.validate_settings(settings)
            
            # Get the actual model name for OpenAI API
            api_model = self.model_mapping.get(model, model)
            
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
                'presence_penalty': validated_settings.get('presence_penalty', 0.0),
                'frequency_penalty': validated_settings.get('frequency_penalty', 0.0),
                'stream': False
            }
            
            # Add optional parameters
            if 'stop' in validated_settings:
                payload['stop'] = validated_settings['stop']
            
            if 'seed' in validated_settings:
                payload['seed'] = validated_settings['seed']
            
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
                raise Exception(f"OpenAI API error: {error_msg}")
                        
        except requests.exceptions.Timeout:
            return self.handle_error(Exception("Request timeout"), "API call")
        except requests.exceptions.RequestException as e:
            return self.handle_error(e, "network request")
        except json.JSONDecodeError as e:
            return self.handle_error(e, "response parsing")
        except Exception as e:
            return self.handle_error(e, "generate_response")
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings specific to OpenAI models"""
        validated = super().validate_settings(settings)
        
        # OpenAI-specific max tokens limits
        max_tokens = validated.get('max_tokens', 2048)
        validated['max_tokens'] = min(max_tokens, 4096)  # OpenAI limit
        
        return validated