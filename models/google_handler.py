"""
Google API handler for Gemini models
Handles communication with Google's Generative AI API endpoints.
"""

import requests
import json
from typing import Dict, Any, List
from .base_handler import BaseHandler

class GoogleHandler(BaseHandler):
    """Handler for Google Gemini models"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model_mapping = {
            'gemini-2.5-pro': 'gemini-2.0-flash-exp',  # Latest available
            'gemini-2.5-flash': 'gemini-2.0-flash-exp',
            'gemini-2.5-flash-lite': 'gemini-1.5-flash',
            'gemini-1.0-ultra': 'gemini-1.5-pro',
            'gemini-pro': 'gemini-1.5-pro'
        }
    
    def generate_response(
        self, 
        model: str, 
        message: str, 
        settings: Dict[str, Any], 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate response using Google Generative AI API"""
        try:
            # Validate and normalize settings
            validated_settings = self.validate_settings(settings)
            
            # Get the actual model name for Google API
            api_model = self.model_mapping.get(model, 'gemini-1.5-pro')
            
            # Format conversation for Google API
            contents = self._format_google_contents(
                conversation_history, 
                message,
                validated_settings.get('system_prompt')
            )
            
            # Prepare request payload
            payload = {
                'contents': contents,
                'generationConfig': {
                    'temperature': validated_settings.get('temperature', 0.7),
                    'maxOutputTokens': validated_settings.get('max_tokens', 2048),
                    'topP': validated_settings.get('top_p', 1.0),
                }
            }
            
            # Add stop sequences if provided
            if 'stop' in validated_settings:
                payload['generationConfig']['stopSequences'] = validated_settings['stop']
            
            # Make API request
            url = f"{self.base_url}/models/{api_model}:generateContent?key={self.api_key}"
            
            response = requests.post(
                url,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and len(data['candidates']) > 0:
                    candidate = data['candidates'][0]
                    if 'content' in candidate and 'parts' in candidate['content']:
                        return candidate['content']['parts'][0]['text']
                    else:
                        raise Exception("No content in response")
                else:
                    raise Exception("No candidates in response")
            else:
                error_data = response.json()
                error_msg = error_data.get('error', {}).get('message', f'HTTP {response.status_code}')
                raise Exception(f"Google API error: {error_msg}")
                        
        except requests.exceptions.Timeout:
            return self.handle_error(Exception("Request timeout"), "API call")
        except requests.exceptions.RequestException as e:
            return self.handle_error(e, "network request")
        except json.JSONDecodeError as e:
            return self.handle_error(e, "response parsing")
        except Exception as e:
            return self.handle_error(e, "generate_response")
    
    def _format_google_contents(
        self, 
        conversation_history: List[Dict[str, str]], 
        current_message: str,
        system_prompt: str = None
    ) -> List[Dict[str, Any]]:
        """Format messages for Google Generative AI API"""
        contents = []
        
        # Add system prompt as first user message if provided
        if system_prompt:
            contents.append({
                'role': 'user',
                'parts': [{'text': f"System: {system_prompt}"}]
            })
            contents.append({
                'role': 'model',
                'parts': [{'text': "I understand. I'll follow these instructions."}]
            })
        
        # Add conversation history
        for msg in conversation_history:
            role = msg.get('sender', 'user')
            content = msg.get('content', '')
            
            # Google uses 'user' and 'model' roles
            if role == 'user':
                contents.append({
                    'role': 'user',
                    'parts': [{'text': content}]
                })
            elif role == 'assistant' or role == 'bot':
                contents.append({
                    'role': 'model',
                    'parts': [{'text': content}]
                })
        
        # Add current message
        contents.append({
            'role': 'user',
            'parts': [{'text': current_message}]
        })
        
        return contents
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings specific to Google models"""
        validated = super().validate_settings(settings)
        
        # Google-specific max tokens limits
        max_tokens = validated.get('max_tokens', 2048)
        validated['max_tokens'] = min(max_tokens, 8192)  # Google limit
        
        # Google doesn't support presence_penalty, frequency_penalty, or seed
        validated.pop('presence_penalty', None)
        validated.pop('frequency_penalty', None)
        validated.pop('seed', None)
        
        return validated