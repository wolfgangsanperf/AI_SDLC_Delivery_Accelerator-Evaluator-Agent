"""
API clients for external services used by the Response Evaluator Agent.
"""
import asyncio
from typing import List, Dict, Optional
from portkey_ai import Portkey

from .config import (
    PORTKEY_API_KEY, PORTKEY_BASE_URL, PORTKEY_PROVIDER, PORTKEY_MODEL,
    DEFAULT_TEMPERATURE, MAX_TOKENS_GENERATION, MAX_TOKENS_SUMMARY,
    MAX_TOKENS_RECOMMENDATIONS, MAX_RETRIES, RETRY_DELAY, logger
)
from .prompts import SYSTEM_PROMPTS


class PortkeyAPIClient:
    """Centralized Portkey API client with error handling and retry logic"""
    
    def __init__(self):
        try:
            self.portkey = Portkey(
                api_key=PORTKEY_API_KEY,
                provider=PORTKEY_PROVIDER,
                base_url=PORTKEY_BASE_URL
            )
            logger.info("Portkey client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Portkey client: {e}")
            raise RuntimeError(f"Failed to initialize Portkey client: {e}")
    
    async def test_connection(self) -> bool:
        """Test the Portkey connection"""
        try:
            await self._call_api(
                messages=[{"role": "user", "content": "test"}],
                context="connection_test"
            )
            return True
        except Exception as e:
            logger.warning(f"Connection test failed: {e}")
            return False
    
    async def _call_api(
        self,
        messages: List[Dict[str, str]],
        context: str = "api_call",
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        retry_count: int = 0
    ) -> str:
        """
        Centralized API call with retry logic and error handling
        
        Args:
            messages: List of messages for the API call
            context: Context for logging (e.g., 'evaluation', 'summary')
            temperature: Temperature override
            max_tokens: Max tokens override
            retry_count: Current retry attempt
            
        Returns:
            Response content as string
            
        Raises:
            Exception: If all retries fail
        """
        try:
            response = self.portkey.chat.completions.create(
                model=PORTKEY_MODEL,
                messages=messages,
                temperature=temperature or DEFAULT_TEMPERATURE,
                max_tokens=max_tokens or MAX_TOKENS_GENERATION
            )
            
            content = response.choices[0].message.content
            logger.info(f"Portkey API call successful for context: {context}")
            return content
            
        except Exception as e:
            logger.error(f"Portkey API call failed for {context} (attempt {retry_count + 1}): {e}")
            
            # Retry logic
            if retry_count < MAX_RETRIES:
                await asyncio.sleep(RETRY_DELAY * (2 ** retry_count))  # Exponential backoff
                return await self._call_api(
                    messages=messages,
                    context=context,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    retry_count=retry_count + 1
                )
            else:
                raise Exception(f"Portkey API failed after {MAX_RETRIES} retries: {str(e)}")
    
    async def call_for_evaluation(self, prompt: str) -> str:
        """Call API for metric evaluation"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["evaluation"]},
            {"role": "user", "content": prompt}
        ]
        return await self._call_api(messages, context="evaluation")
    
    async def call_for_summary(self, prompt: str) -> str:
        """Call API for summary generation"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["summary"]},
            {"role": "user", "content": prompt}
        ]
        return await self._call_api(messages, context="summary", max_tokens=MAX_TOKENS_SUMMARY)
    
    async def call_for_recommendations(self, prompt: str) -> str:
        """Call API for recommendations generation"""
        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS["recommendations"]},
            {"role": "user", "content": prompt}
        ]
        return await self._call_api(messages, context="recommendations", max_tokens=MAX_TOKENS_RECOMMENDATIONS)
    
    async def call_with_system_prompt(self, system_prompt: str, user_message: str) -> str:
        """Call API with custom system prompt"""
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]
        return await self._call_api(messages, context="custom_evaluation")
