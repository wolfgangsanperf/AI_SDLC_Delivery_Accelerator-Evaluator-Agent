"""
Configuration settings and constants for the Response Evaluator Agent API.
"""
import os
import logging
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class ApiConfig:
    """API server configuration"""
    title: str = "Response Evaluator Agent"
    description: str = "Evaluate generated content using LLM-as-a-judge methodology"
    version: str = "1.0.0"
    host: str = os.getenv("API_HOST", "0.0.0.0")
    port: int = int(os.getenv("API_PORT", "8040"))
    reload: bool = os.getenv("API_RELOAD", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "info")

@dataclass
class RetryConfig:
    """Configuration for retry operations"""
    max_retries: int = int(os.getenv("MAX_RETRIES", "3"))
    retry_delay: float = float(os.getenv("RETRY_DELAY", "1.0"))
    exponential_backoff: bool = os.getenv("EXPONENTIAL_BACKOFF", "true").lower() == "true"

@dataclass
class ProviderConfig:
    """LLM Provider configuration"""
    endpoint: str = os.getenv("PORTKEY_BASE_URL", "https://portkeygateway.perficient.com/v1")
    api_key: str = os.getenv("PORTKEY_API_KEY", "")
    llm_model: str = os.getenv("PORTKEY_MODEL", "gpt-4o-mini")
    llm_model_provider: str = os.getenv("PORTKEY_PROVIDER", "@azure-openai")

@dataclass
class BehaviourConfig:
    """Application behavior configuration"""
    default_temperature: float = float(os.getenv("DEFAULT_TEMPERATURE", "0.6"))
    max_tokens_generation: int = int(os.getenv("MAX_TOKENS_GENERATION", "2000"))
    max_tokens_summary: int = int(os.getenv("MAX_TOKENS_SUMMARY", "200"))
    max_tokens_recommendations: int = int(os.getenv("MAX_TOKENS_RECOMMENDATIONS", "300"))

@dataclass
class EvaluationConfig:
    """Evaluation-specific configuration"""
    deepeval_threshold: float = float(os.getenv("DEEPEVAL_THRESHOLD", "0.7"))
    hallucination_threshold: float = float(os.getenv("HALLUCINATION_THRESHOLD", "0.8"))
    context_similarity_threshold: float = float(os.getenv("CONTEXT_SIMILARITY_THRESHOLD", "0.7"))
    factual_confidence_threshold: float = float(os.getenv("FACTUAL_CONFIDENCE_THRESHOLD", "0.6"))
    
    # Evaluation metric weights
    metric_weights: Dict[str, float] = None
    
    def __post_init__(self):
        """Initialize metric weights after dataclass creation"""
        if self.metric_weights is None:
            self.metric_weights = {
                "relevance": 0.18,
                "accuracy": 0.15,
                "completeness": 0.15,
                "clarity": 0.12,
                "structure": 0.08,
                "consistency": 0.08,
                "hallucination_detection": 0.12,
                "context_adherence": 0.08,
                "factual_grounding": 0.04
            }

@dataclass
class LoggingConfig:
    """Logging configuration"""
    level: str = os.getenv("LOG_LEVEL", "INFO")
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_name: str = os.getenv("LOG_FILE", "evaluation_results.log")
    console_logging: bool = os.getenv("CONSOLE_LOGGING", "true").lower() == "true"

class Config:
    """Main configuration class"""
    def __init__(self):
        self.api = ApiConfig()
        self.provider = ProviderConfig()
        self.retry = RetryConfig()
        self.behaviour = BehaviourConfig()
        self.evaluation = EvaluationConfig()
        self.logging = LoggingConfig()
        
        # Setup logging with the current configuration
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """Configure logging for the application"""
        handlers = []
        
        # Add file handler
        handlers.append(logging.FileHandler(self.logging.file_name))
        
        # Add console handler if enabled
        if self.logging.console_logging:
            handlers.append(logging.StreamHandler())
        
        logging.basicConfig(
            level=getattr(logging, self.logging.level.upper()),
            format=self.logging.format,
            handlers=handlers,
            force=True  # Override any existing logging configuration
        )
        
        return logging.getLogger(__name__)

# Global configuration instance
config = Config()

# Backward compatibility - Export commonly used values
API_TITLE = config.api.title
API_DESCRIPTION = config.api.description
API_VERSION = config.api.version
HOST = config.api.host
PORT = config.api.port
RELOAD = config.api.reload
LOG_LEVEL = config.api.log_level

PORTKEY_API_KEY = config.provider.api_key
PORTKEY_BASE_URL = config.provider.endpoint
PORTKEY_PROVIDER = config.provider.llm_model_provider
PORTKEY_MODEL = config.provider.llm_model

DEFAULT_TEMPERATURE = config.behaviour.default_temperature
MAX_TOKENS_GENERATION = config.behaviour.max_tokens_generation
MAX_TOKENS_SUMMARY = config.behaviour.max_tokens_summary
MAX_TOKENS_RECOMMENDATIONS = config.behaviour.max_tokens_recommendations

MAX_RETRIES = config.retry.max_retries
RETRY_DELAY = config.retry.retry_delay

METRIC_WEIGHTS = config.evaluation.metric_weights
DEEPEVAL_THRESHOLD = config.evaluation.deepeval_threshold
HALLUCINATION_THRESHOLD = config.evaluation.hallucination_threshold
CONTEXT_SIMILARITY_THRESHOLD = config.evaluation.context_similarity_threshold
FACTUAL_CONFIDENCE_THRESHOLD = config.evaluation.factual_confidence_threshold

logger = config.logger
