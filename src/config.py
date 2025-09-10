"""
Configuration settings and constants for the Response Evaluator Agent API.
"""
import os
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
API_TITLE = "Response Evaluator Agent"
API_DESCRIPTION = "Evaluate generated content using LLM-as-a-judge methodology"
API_VERSION = "1.0.0"

# Server Configuration
HOST = "0.0.0.0"
PORT = 8040
RELOAD = True
LOG_LEVEL = "info"

# Portkey Configuration
PORTKEY_API_KEY = os.getenv("PORTKEY_API_KEY")
PORTKEY_BASE_URL = os.getenv("PORTKEY_BASE_URL")
PORTKEY_PROVIDER = "@azure-openai"
PORTKEY_MODEL = "gpt-4o-mini"

# API Client Configuration
DEFAULT_TEMPERATURE = 0.6
MAX_TOKENS_GENERATION = 2000
MAX_TOKENS_SUMMARY = 200
MAX_TOKENS_RECOMMENDATIONS = 300
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# Evaluation Weights
METRIC_WEIGHTS = {
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

# Hallucination Detection Configuration
HALLUCINATION_THRESHOLD = 0.8  # Higher threshold for hallucination detection
CONTEXT_SIMILARITY_THRESHOLD = 0.7  # Minimum similarity to context for adherence
FACTUAL_CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for factual claims

# DeepEval Configuration
DEEPEVAL_THRESHOLD = 0.7

# Logging Configuration
def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('evaluation_results.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

logger = setup_logging()
