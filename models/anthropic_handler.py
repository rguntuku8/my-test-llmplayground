"""
Anthropic API handler for Claude models
Handles communication with Anthropic's API endpoints.
"""

import requests
import json
from typing import Dict, Any, List
from .base_handler import BaseHandler

class AnthropicHandler(BaseHandler):
    """Handler for Anthropic Claude models"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api.anthropic.com/v1"
        self.model_mapping = {
            'claude-3-5-sonnet': 'claude-3-5-sonnet-20241022',
            'claude-3-5-haiku': 'claude-3-5-haiku-20241022',
            'claude-3-opus': 'claude-3-opus-20240229',
            'claude-3-haiku': 'claude-3-haiku-20240307'
        }
    
    def generate_response(
        self, 
        model: str, 
        message: str, 
        settings: Dict[str, Any], 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate response using Anthropic API"""
        try:
            # Validate and normalize settings
            validated_settings = self.validate_settings(settings)
            
            # Get the actual model name for Anthropic API
            api_model = self.model_mapping.get(model, model)
            
            # Format messages for Anthropic (they use a different format)
            messages = self._format_anthropic_messages(
                conversation_history, 
                message
            )
            
            # Prepare request payload
            payload = {
                'model': api_model,
                'messages': messages,
                'max_tokens': validated_settings.get('max_tokens', 2048),
                'temperature': validated_settings.get('temperature', 0.7),
                'top_p': validated_settings.get('top_p', 1.0)
            }
            
            # Add system prompt if provided
            system_prompt = validated_settings.get('system_prompt')
            if system_prompt:
                payload['system'] = system_prompt
            
            # Add stop sequences if provided
            if 'stop' in validated_settings:
                payload['stop_sequences'] = validated_settings['stop']
            
            # Make API request
            headers = {
                'x-api-key': self.api_key,
                'Content-Type': 'application/json',
                'anthropic-version': '2023-06-01'
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                return data['content'][0]['text']
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                raise Exception(f"Anthropic API error: {error_msg}")
                        
        except requests.exceptions.Timeout:
            return self.handle_error(Exception("Request timeout"), "API call")
        except requests.exceptions.RequestException as e:
            return self.handle_error(e, "network request")
        except json.JSONDecodeError as e:
            return self.handle_error(e, "response parsing")
        except Exception as e:
            return self.handle_error(e, "generate_response")
    
    def _format_anthropic_messages(
        self, 
        conversation_history: List[Dict[str, str]], 
        current_message: str
    ) -> List[Dict[str, str]]:
        """Format messages for Anthropic API (no system role in messages)"""
        messages = []
        
        # Add conversation history
        for msg in conversation_history:
            role = msg.get('sender', 'user')
            content = msg.get('content', '')
            
            # Anthropic uses 'user' and 'assistant' roles
            if role == 'user':
                messages.append({'role': 'user', 'content': content})
            elif role == 'assistant' or role == 'bot':
                messages.append({'role': 'assistant', 'content': content})
        
        # Add current message
        messages.append({'role': 'user', 'content': current_message})
        
        return messages
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings specific to Anthropic models"""
        validated = super().validate_settings(settings)
        
        # Anthropic-specific max tokens limits
        max_tokens = validated.get('max_tokens', 2048)
        validated['max_tokens'] = min(max_tokens, 8192)  # Anthropic limit
        
        # Anthropic doesn't support presence_penalty and frequency_penalty
        validated.pop('presence_penalty', None)
        validated.pop('frequency_penalty', None)
        validated.pop('seed', None)  # Anthropic doesn't support seed
        
        return validated