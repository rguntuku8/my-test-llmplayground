"""
Hugging Face API handler for open-source models
Handles communication with Hugging Face's Inference API endpoints.
"""

import requests
import json
from typing import Dict, Any, List
from .base_handler import BaseHandler

class HuggingFaceHandler(BaseHandler):
    """Handler for Hugging Face models"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = "https://api-inference.huggingface.co/models"
        # Default models for different categories
        self.default_models = {
            'text-generation': 'microsoft/DialoGPT-large',
            'conversational': 'microsoft/DialoGPT-large',
            'chat': 'HuggingFaceH4/zephyr-7b-beta'
        }
    
    def generate_response(
        self, 
        model: str, 
        message: str, 
        settings: Dict[str, Any], 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """Generate response using Hugging Face Inference API"""
        try:
            # Validate and normalize settings
            validated_settings = self.validate_settings(settings)
            
            # Use a default chat model for now
            api_model = self.default_models['chat']
            
            # Format the conversation for Hugging Face
            formatted_input = self._format_hf_input(
                conversation_history, 
                message,
                validated_settings.get('system_prompt')
            )
            
            # Prepare request payload
            payload = {
                'inputs': formatted_input,
                'parameters': {
                    'temperature': validated_settings.get('temperature', 0.7),
                    'max_new_tokens': validated_settings.get('max_tokens', 512),  # HF uses max_new_tokens
                    'top_p': validated_settings.get('top_p', 1.0),
                    'do_sample': True,
                    'return_full_text': False
                }
            }
            
            # Add stop sequences if provided
            if 'stop' in validated_settings:
                payload['parameters']['stop_sequences'] = validated_settings['stop']
            
            # Make API request
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                f"{self.base_url}/{api_model}",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get('generated_text', '').strip()
                elif isinstance(data, dict):
                    return data.get('generated_text', '').strip()
                else:
                    raise Exception("Unexpected response format")
            else:
                error_data = response.json()
                error_msg = error_data.get('error', f'HTTP {response.status_code}')
                raise Exception(f"Hugging Face API error: {error_msg}")
                        
        except requests.exceptions.Timeout:
            return self.handle_error(Exception("Request timeout"), "API call")
        except requests.exceptions.RequestException as e:
            return self.handle_error(e, "network request")
        except json.JSONDecodeError as e:
            return self.handle_error(e, "response parsing")
        except Exception as e:
            return self.handle_error(e, "generate_response")
    
    def _format_hf_input(
        self, 
        conversation_history: List[Dict[str, str]], 
        current_message: str,
        system_prompt: str = None
    ) -> str:
        """Format conversation for Hugging Face models"""
        formatted_parts = []
        
        # Add system prompt if provided
        if system_prompt:
            formatted_parts.append(f"System: {system_prompt}")
        
        # Add conversation history
        for msg in conversation_history:
            role = msg.get('sender', 'user')
            content = msg.get('content', '')
            
            if role == 'user':
                formatted_parts.append(f"Human: {content}")
            elif role == 'assistant' or role == 'bot':
                formatted_parts.append(f"Assistant: {content}")
        
        # Add current message
        formatted_parts.append(f"Human: {current_message}")
        formatted_parts.append("Assistant:")
        
        return "\n".join(formatted_parts)
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """Validate settings specific to Hugging Face models"""
        validated = super().validate_settings(settings)
        
        # Hugging Face-specific max tokens limits (usually smaller)
        max_tokens = validated.get('max_tokens', 512)
        validated['max_tokens'] = min(max_tokens, 1024)  # Conservative limit for HF
        
        # Hugging Face doesn't support presence_penalty, frequency_penalty, or seed
        validated.pop('presence_penalty', None)
        validated.pop('frequency_penalty', None)
        validated.pop('seed', None)
        
        return validated