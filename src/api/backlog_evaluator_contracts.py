"""
Pydantic models for the Response Evaluator Agent API.
"""
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field


class GeneratedContent(BaseModel):
    """Generated content structure"""
    title: str
    formatted_output: str


class ContextItem(BaseModel):
    """Context item structure"""
    content: str


class EvaluationInput(BaseModel):
    """Input model matching your exact structure"""
    session_id: str
    backlog_type: str
    user_prompt: str
    system_prompt: str = Field(..., description="System prompt for evaluation instructions")
    generated_content: GeneratedContent
    context: List[ContextItem]
    template: str = Field(..., description="Template with format instructions that the generated content should follow")


class EvaluationMetric(str, Enum):
    """Available evaluation metrics"""
    RELEVANCE = "relevance"
    ACCURACY = "accuracy"
    COMPLETENESS = "completeness"
    CLARITY = "clarity"
    STRUCTURE = "structure"
    CONSISTENCY = "consistency"
    HALLUCINATION_DETECTION = "hallucination_detection"
    CONTEXT_ADHERENCE = "context_adherence"
    FACTUAL_GROUNDING = "factual_grounding"


class MetricScore(BaseModel):
    """Score for a specific metric"""
    metric: str
    score: float = Field(..., ge=0.0, le=1.0, description="Score between 0 and 1")
    reasoning: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the score")
    
    def model_dump(self, **kwargs):
        """Custom serialization to exclude reasoning field when None"""
        data = super().model_dump(**kwargs)
        if data.get('reasoning') is None:
            data.pop('reasoning', None)
        return data
    
    def dict(self, **kwargs):
        """For backward compatibility with older Pydantic versions"""
        data = super().dict(**kwargs)
        if data.get('reasoning') is None:
            data.pop('reasoning', None)
        return data


class EvaluationResult(BaseModel):
    """Result of evaluation"""
    session_id: str
    overall_score: float = Field(..., ge=0.0, le=1.0)
    metric_scores: List[MetricScore]
    summary: str
    recommendations: str
    evaluation_timestamp: str
    evaluation_metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluationMetadata(BaseModel):
    """Evaluation metadata with performance metrics"""
    tokens_used: int = Field(..., description="Tokens used during evaluation")
    tokens_generated: int = Field(..., description="Tokens generated during evaluation")
    evaluation_time_ms: int = Field(..., description="Duration of evaluation in milliseconds")


class EvaluationResponseBody(BaseModel):
    """Evaluation response body following the new specification"""
    session_id: str
    backlog_type: str
    status: str = Field(..., description="Status of generation")
    evaluation_metrics: Dict[str, Any] = Field(default_factory=dict, description="Evaluation metrics data")
    evaluation_metadata: EvaluationMetadata


class StandardizedEvaluationResponse(BaseModel):
    """Standardized evaluation response following the specified format"""
    status: int = Field(..., description="HTTP status code")
    timestamp: str
    message: str
    body: EvaluationResponseBody


class GeneratorModel(BaseModel):
    """Generator model information"""
    name: str
    status: str = "loaded"


class HealthCheckBody(BaseModel):
    """Health check response body"""
    status: str
    generator_model: GeneratorModel


class HealthCheckResponse(BaseModel):
    """Health check response following the specified format"""
    status: int = Field(..., description="HTTP status code")
    timestamp: str
    message: str
    body: HealthCheckBody
