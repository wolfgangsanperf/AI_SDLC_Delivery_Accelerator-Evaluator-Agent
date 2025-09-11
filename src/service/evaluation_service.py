"""
Business Service for Evaluation Operations.

This module contains the core business logic for content evaluation,
separated from the API layer concerns.
"""
from typing import Dict, Any
from src.api.backlog_evaluator_contracts import EvaluationInput, EvaluationResult
from src.service.evaluators import DeepEvalEvaluator
from src.config.config import logger


class EvaluationService:
    """Service class that handles the business logic for content evaluation."""
    
    def __init__(self):
        """Initialize the evaluation service with required components."""
        self.evaluator = DeepEvalEvaluator()
    
    async def evaluate_content(self, evaluation_input: EvaluationInput) -> EvaluationResult:
        """
        Evaluate content using the configured evaluator.
        
        Args:
            evaluation_input: The content and context to evaluate
            
        Returns:
            EvaluationResult: Complete evaluation results
            
        Raises:
            Exception: If evaluation fails
        """
        try:
            logger.info(f"Service: Starting evaluation for session: {evaluation_input.session_id}")
            
            # Perform evaluation using the DeepEval evaluator
            result = await self.evaluator.evaluate_all(evaluation_input)
            
            logger.info(f"Service: Evaluation completed for session: {evaluation_input.session_id}")
            return result
            
        except Exception as e:
            logger.error(f"Service: Evaluation failed for session {evaluation_input.session_id}: {str(e)}")
            raise e
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Check the health status of the evaluation service.
        
        Returns:
            Dict containing health status information
        """
        try:
            # You can add more sophisticated health checks here
            # For example, check database connections, external APIs, etc.
            
            # Basic health check - verify evaluator is initialized
            is_healthy = self.evaluator is not None
            
            # You could also test API connections here
            # connection_ok = await self.evaluator.api_client.test_connection()
            # is_healthy = is_healthy and connection_ok
            
            return {
                "is_healthy": is_healthy,
                "service_status": "operational" if is_healthy else "degraded",
                "components": {
                    "evaluator": "healthy" if self.evaluator is not None else "unhealthy"
                }
            }
            
        except Exception as e:
            logger.error(f"Service: Health check failed: {str(e)}")
            return {
                "is_healthy": False,
                "service_status": "error",
                "error": str(e)
            }
    
    async def get_metrics_info(self) -> Dict[str, Any]:
        """
        Get information about available evaluation metrics and their weights.
        
        Returns:
            Dict containing metrics information
        """
        try:
            # This could be moved to a configuration or metadata service
            # For now, keeping the same structure as the original implementation
            return {
                "metrics": [
                    {
                        "name": "relevance",
                        "weight": 0.18,
                        "description": "How well the content addresses the user's prompt"
                    },
                    {
                        "name": "accuracy", 
                        "weight": 0.15,
                        "description": "Factual correctness and technical accuracy"
                    },
                    {
                        "name": "completeness",
                        "weight": 0.15, 
                        "description": "Whether all necessary sections are included"
                    },
                    {
                        "name": "clarity",
                        "weight": 0.12,
                        "description": "Readability and professional language"
                    },
                    {
                        "name": "structure",
                        "weight": 0.08,
                        "description": "Proper formatting and organization"
                    },
                    {
                        "name": "consistency",
                        "weight": 0.08,
                        "description": "Internal consistency and alignment with context"
                    },
                    {
                        "name": "hallucination_detection",
                        "weight": 0.12,
                        "description": "Identifies and penalizes fabricated or unsupported claims"
                    },
                    {
                        "name": "context_adherence",
                        "weight": 0.08,
                        "description": "Alignment with provided contextual information"
                    },
                    {
                        "name": "factual_grounding",
                        "weight": 0.04,
                        "description": "Verification of claims against reliable sources"
                    }
                ],
                "scoring": {
                    "range": "0.0 to 1.0",
                    "excellent": "> 0.8",
                    "good": "0.7 - 0.8", 
                    "needs_improvement": "< 0.7"
                }
            }
            
        except Exception as e:
            logger.error(f"Service: Failed to get metrics info: {str(e)}")
            raise e
