"""
API Controller for the Backlog Evaluator endpoints.

This module contains the FastAPI route definitions and handles HTTP request/response logic,
delegating business logic to the service layer.
"""
import time
from datetime import datetime
from fastapi import APIRouter, HTTPException

from .backlog_evaluator_contracts import (
    EvaluationInput, 
    StandardizedEvaluationResponse, 
    HealthCheckResponse, 
    HealthCheckBody, 
    GeneratorModel, 
    EvaluationResponseBody, 
    EvaluationMetadata
)
from src.service.evaluators import DeepEvalEvaluator
from src.service.evaluation_service import EvaluationService
from src.config.config import (
    logger, PORTKEY_MODEL
)

# Create router
router = APIRouter(prefix="/api/validate", tags=["backlog-evaluator"])

# Initialize evaluation service
evaluation_service = EvaluationService()


@router.post("/backlog-item-generated", response_model=StandardizedEvaluationResponse)
async def evaluate_content(evaluation_input: EvaluationInput):
    """
    Evaluate generated content based on multiple quality metrics.
    
    Args:
        evaluation_input: The content and context to evaluate
        
    Returns:
        StandardizedEvaluationResponse: Evaluation results in standardized format
    """
    start_time = time.time()
    
    try:
        logger.info(f"Starting evaluation for session: {evaluation_input.session_id}")
        
        # Delegate to service layer
        result = await evaluation_service.evaluate_content(evaluation_input)
        
        # Calculate evaluation time
        end_time = time.time()
        evaluation_time_ms = int((end_time - start_time) * 1000)
        
        # Estimate token usage (these would typically come from the actual LLM API calls)
        estimated_tokens_used = len(evaluation_input.user_prompt.split()) * 2  # Rough estimation
        estimated_tokens_generated = len(result.summary.split()) * 2  # Rough estimation
        
        # Create evaluation metrics dictionary from the metric scores
        evaluation_metrics = {
            "overall_score": result.overall_score,
            "metric_scores": [score.model_dump() for score in result.metric_scores],
            "summary": result.summary,
            "recommendations": result.recommendations
        }
        
        # Create the response body
        response_body = EvaluationResponseBody(
            session_id=evaluation_input.session_id,
            backlog_type=evaluation_input.backlog_type,
            status="completed",
            evaluation_metrics=evaluation_metrics,
            evaluation_metadata=EvaluationMetadata(
                tokens_used=estimated_tokens_used,
                tokens_generated=estimated_tokens_generated,
                evaluation_time_ms=evaluation_time_ms
            )
        )
        
        logger.info(f"Evaluation completed for session: {evaluation_input.session_id}, Overall score: {result.overall_score:.3f}")
        
        return StandardizedEvaluationResponse(
            status=200,
            timestamp=datetime.now().isoformat(),
            message="Evaluation completed successfully",
            body=response_body
        )
        
    except Exception as e:
        # Calculate evaluation time even on failure
        end_time = time.time()
        evaluation_time_ms = int((end_time - start_time) * 1000)
        
        logger.error(f"Evaluation failed for session {evaluation_input.session_id}: {str(e)}")
        
        # Create error response body
        error_response_body = EvaluationResponseBody(
            session_id=evaluation_input.session_id,
            backlog_type=evaluation_input.backlog_type,
            status="failed",
            evaluation_metrics={"error": str(e)},
            evaluation_metadata=EvaluationMetadata(
                tokens_used=0,
                tokens_generated=0,
                evaluation_time_ms=evaluation_time_ms
            )
        )
        
        return StandardizedEvaluationResponse(
            status=500,
            timestamp=datetime.now().isoformat(),
            message=f"Evaluation failed: {str(e)}",
            body=error_response_body
        )


@router.get("/health", response_model=HealthCheckResponse)
async def validate_health():
    """
    Backlog Core compatible health check endpoint.
    
    Returns health status in the format expected by the Backlog Core system,
    including generator model information and standardized response structure.
    
    Returns:
        HealthCheckResponse: Structured health check response with status, timestamp, message, and body
    """
    try:
        # Delegate to service layer
        health_status = await evaluation_service.check_health()
        
        return HealthCheckResponse(
            status=200 if health_status["is_healthy"] else 503,
            timestamp=datetime.now().isoformat(),
            message="Health check passed successfully" if health_status["is_healthy"] else "Service is unhealthy",
            body=HealthCheckBody(
                status="healthy" if health_status["is_healthy"] else "unhealthy",
                generator_model=GeneratorModel(
                    name=PORTKEY_MODEL,
                    status="loaded" if health_status["is_healthy"] else "error"
                )
            )
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return HealthCheckResponse(
            status=500,
            timestamp=datetime.now().isoformat(),
            message=f"Health check failed: {str(e)}",
            body=HealthCheckBody(
                status="error",
                generator_model=GeneratorModel(
                    name=PORTKEY_MODEL,
                    status="error"
                )
            )
        )


@router.get("/metrics/info")
async def get_metrics_info():
    """
    Get information about available evaluation metrics and their weights.
    
    Returns:
        dict: Metrics information including descriptions and weights
    """
    # Delegate to service layer
    return await evaluation_service.get_metrics_info()
