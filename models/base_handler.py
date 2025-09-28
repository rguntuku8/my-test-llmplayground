"""
Base handler class for all AI model providers
Defines the common interface and shared functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)

class BaseHandler(ABC):
    """Abstract base class for all model handlers"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.provider_name = self.__class__.__name__.replace('Handler', '').lower()
        
    @abstractmethod
    def generate_response(
        self, 
        model: str, 
        message: str, 
        settings: Dict[str, Any], 
        conversation_history: List[Dict[str, str]]
    ) -> str:
        """
        Generate response from the AI model
        
        Args:
            model: The specific model to use
            message: The user's message
            settings: Model parameters (temperature, max_tokens, etc.)
            conversation_history: Previous conversation messages
            
        Returns:
            Generated response string
        """
        pass
    
    def validate_settings(self, settings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize settings for the model
        
        Args:
            settings: Raw settings from frontend
            
        Returns:
            Validated and normalized settings
        """
        validated = {}
        
        # Temperature (0.0 to 2.0)
        temperature = settings.get('temperature', 0.7)
        validated['temperature'] = max(0.0, min(2.0, float(temperature)))
        
        # Max tokens (1 to 4096, model-dependent)
        max_tokens = settings.get('maxTokens', 2048)
        validated['max_tokens'] = max(1, min(4096, int(max_tokens)))
        
        # Top P (0.0 to 1.0)
        top_p = settings.get('topP', 1.0)
        validated['top_p'] = max(0.0, min(1.0, float(top_p)))
        
        # Presence penalty (-2.0 to 2.0)
        presence_penalty = settings.get('presencePenalty', 0.0)
        validated['presence_penalty'] = max(-2.0, min(2.0, float(presence_penalty)))
        
        # Frequency penalty (-2.0 to 2.0)
        frequency_penalty = settings.get('frequencyPenalty', 0.0)
        validated['frequency_penalty'] = max(-2.0, min(2.0, float(frequency_penalty)))
        
        # Stop sequences
        stop_sequence = settings.get('stopSequence', '')
        if stop_sequence and stop_sequence.strip():
            validated['stop'] = [s.strip() for s in stop_sequence.split(',') if s.strip()]
        
        # System prompt
        system_prompt = settings.get('systemPrompt', '')
        if system_prompt and system_prompt.strip():
            validated['system_prompt'] = system_prompt.strip()
        
        # Seed (for reproducibility)
        seed = settings.get('seed')
        if seed is not None and str(seed).strip():
            try:
                validated['seed'] = int(seed)
            except (ValueError, TypeError):
                pass  # Ignore invalid seed values
        
        return validated
    
    def format_conversation_history(
        self, 
        conversation_history: List[Dict[str, str]], 
        system_prompt: Optional[str] = None
    ) -> List[Dict[str, str]]:
        """
        Format conversation history for the specific provider
        
        Args:
            conversation_history: List of message dictionaries
            system_prompt: Optional system prompt to include
            
        Returns:
            Formatted conversation history
        """
        messages = []
        
        # Add system prompt if provided
        if system_prompt:
            messages.append({
                'role': 'system',
                'content': system_prompt
            })
        
        # Add conversation history
        for msg in conversation_history:
            role = msg.get('sender', 'user')
            content = msg.get('content', '')
            
            # Normalize role names
            if role == 'user':
                messages.append({'role': 'user', 'content': content})
            elif role == 'assistant' or role == 'bot':
                messages.append({'role': 'assistant', 'content': content})
        
        return messages
    
    def handle_error(self, error: Exception, context: str = "") -> str:
        """
        Handle and log errors consistently
        
        Args:
            error: The exception that occurred
            context: Additional context about where the error occurred
            
        Returns:
            User-friendly error message
        """
        error_msg = str(error)
        log_msg = f"{self.provider_name} error"
        if context:
            log_msg += f" in {context}"
        log_msg += f": {error_msg}"
        
        logger.error(log_msg)
        
        # Return user-friendly error message
        if "rate limit" in error_msg.lower():
            return f"Rate limit exceeded for {self.provider_name}. Please try again later."
        elif "api key" in error_msg.lower() or "unauthorized" in error_msg.lower():
            return f"Authentication failed for {self.provider_name}. Please check your API key."
        elif "quota" in error_msg.lower() or "billing" in error_msg.lower():
            return f"Quota exceeded for {self.provider_name}. Please check your billing status."
        else:
            return f"Error from {self.provider_name}: {error_msg}"