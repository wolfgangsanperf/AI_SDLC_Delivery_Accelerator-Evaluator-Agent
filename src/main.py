"""
Main FastAPI application for the Response Evaluator Agent API.

This API evaluates generated content using LLM-as-a-judge methodology,
providing detailed scoring across multiple quality metrics.
"""
import uuid
import time
from datetime import datetime

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .models import EvaluationInput, StandardizedEvaluationResponse, HealthCheckResponse, HealthCheckBody, GeneratorModel, EvaluationResponseBody, EvaluationMetadata
from .evaluators import DeepEvalEvaluator
from .config import API_TITLE, API_DESCRIPTION, API_VERSION, HOST, PORT, RELOAD, LOG_LEVEL, logger, PORTKEY_MODEL


# Initialize FastAPI application
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/evaluate", response_model=StandardizedEvaluationResponse)
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
        
        # Initialize evaluator
        evaluator = DeepEvalEvaluator()
        
        # Perform evaluation
        result = await evaluator.evaluate_all(evaluation_input)
        
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


@app.get("/validate/health", response_model=HealthCheckResponse)
async def validate_health():
    """
    Backlog Core compatible health check endpoint.
    
    Returns health status in the format expected by the Backlog Core system,
    including generator model information and standardized response structure.
    
    Returns:
        HealthCheckResponse: Structured health check response with status, timestamp, message, and body
    """
    try:
        # Check if the service is healthy (you can add more checks here)
        is_healthy = True
        
        if is_healthy:
            return HealthCheckResponse(
                status=200,
                timestamp=datetime.now().isoformat(),
                message="Health check passed successfully",
                body=HealthCheckBody(
                    status="healthy",
                    generator_model=GeneratorModel(
                        name=PORTKEY_MODEL,
                        status="loaded"
                    )
                )
            )
        else:
            return HealthCheckResponse(
                status=503,
                timestamp=datetime.now().isoformat(),
                message="Service is unhealthy",
                body=HealthCheckBody(
                    status="unhealthy",
                    generator_model=GeneratorModel(
                        name=PORTKEY_MODEL,
                        status="error"
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


@app.get("/metrics/info")
async def get_metrics_info():
    """
    Get information about available evaluation metrics and their weights.
    
    Returns:
        dict: Metrics information including descriptions and weights
    """
    return {
        "metrics": [
            {
                "name": "relevance",
                "weight": 0.25,
                "description": "How well the content addresses the user's prompt"
            },
            {
                "name": "accuracy", 
                "weight": 0.20,
                "description": "Factual correctness and technical accuracy"
            },
            {
                "name": "completeness",
                "weight": 0.20, 
                "description": "Whether all necessary sections are included"
            },
            {
                "name": "clarity",
                "weight": 0.15,
                "description": "Readability and professional language"
            },
            {
                "name": "structure",
                "weight": 0.10,
                "description": "Proper formatting and organization"
            },
            {
                "name": "consistency",
                "weight": 0.10,
                "description": "Internal consistency and alignment with context"
            }
        ],
        "scoring": {
            "range": "0.0 to 1.0",
            "excellent": "> 0.8",
            "good": "0.7 - 0.8", 
            "needs_improvement": "< 0.7"
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
        log_level=LOG_LEVEL
    )
