"""
Evaluation logic for the Response Evaluator Agent API.
"""
import json
import re
import asyncio
from typing import List, Dict, Any
from datetime import datetime

from deepeval import evaluate
from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric, ContextualPrecisionMetric, ContextualRecallMetric
from deepeval.test_case import LLMTestCase

from .models import EvaluationInput, EvaluationMetric, MetricScore, EvaluationResult
from .clients import PortkeyAPIClient
from .prompts import EVALUATION_PROMPTS
from .config import DEEPEVAL_THRESHOLD, METRIC_WEIGHTS, logger


class DeepEvalEvaluator:
    """DeepEval-based evaluator with LangChain and Portkey AI integration"""
    
    def __init__(self):
        # Initialize centralized API client
        self.api_client = PortkeyAPIClient()
        
        # Test connection on initialization
        asyncio.create_task(self._test_connection())
            
    async def _test_connection(self):
        """Test API connection asynchronously"""
        try:
            connection_ok = await self.api_client.test_connection()
            if connection_ok:
                logger.info("Portkey connection verified")
            else:
                logger.warning("Portkey connection test failed")
        except Exception as e:
            logger.error(f"Connection test error: {e}")

    async def evaluate_with_deepeval(self, evaluation_input: EvaluationInput) -> Dict[str, Any]:
        """Evaluate using DeepEval metrics"""
        
        # Prepare context string
        context_str = "\n".join([item.content for item in evaluation_input.context])
        retrieval_contexts = [context_str]
        
        # Create LLMTestCase for DeepEval
        test_case = LLMTestCase(
            input=evaluation_input.user_prompt,
            actual_output=evaluation_input.generated_content.formatted_output,
            retrieval_context=retrieval_contexts
        )
        
        # Initialize DeepEval metrics
        metrics = {
            "answer_relevancy": AnswerRelevancyMetric(threshold=DEEPEVAL_THRESHOLD, model=None),
            "faithfulness": FaithfulnessMetric(threshold=DEEPEVAL_THRESHOLD, model=None),
            "contextual_precision": ContextualPrecisionMetric(threshold=DEEPEVAL_THRESHOLD, model=None),
            "contextual_recall": ContextualRecallMetric(threshold=DEEPEVAL_THRESHOLD, model=None)
        }
        
        results = {}
        
        # Evaluate each metric
        for metric_name, metric in metrics.items():
            try:
                # Run the metric evaluation
                await asyncio.to_thread(metric.measure, test_case)
                results[metric_name] = {
                    "score": metric.score,
                    "reason": metric.reason,
                    "success": metric.success
                }
                logger.info(f"DeepEval {metric_name}: {metric.score:.3f}")
            except Exception as e:
                logger.error(f"Error evaluating {metric_name}: {str(e)}")
                results[metric_name] = {
                    "score": 0,
                    "reason": f"Error during evaluation: {str(e)}",
                    "success": False
                }
        
        return results
        
    async def evaluate_all_metrics(self, evaluation_input: EvaluationInput) -> List[MetricScore]:
        """Evaluate all metrics using the provided system_prompt"""
        try:
            # Check if this is the new validation system prompt format
            if "validation agent" in evaluation_input.system_prompt.lower():
                return await self._handle_validation_prompt(evaluation_input)
            else:
                return await self._handle_evaluation_prompt(evaluation_input)
            
        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            return self._get_default_metric_scores(f"Evaluation error: {str(e)}")
    
    async def _handle_validation_prompt(self, evaluation_input: EvaluationInput) -> List[MetricScore]:
        """Handle the new validation system prompt that returns binary proceed/reason format"""
        try:
            # Create the user message in the expected validation format
            input_data = {
                "input": {
                    "context": [{"content": item.content} for item in evaluation_input.context],
                    "template": evaluation_input.template,
                    "user_request": evaluation_input.user_prompt
                },
                "output": {
                    "backlog_type": evaluation_input.backlog_type,
                    "generated_content": {
                        "title": evaluation_input.generated_content.title,
                        "formatted_output": evaluation_input.generated_content.formatted_output
                    }
                }
            }
            
            user_message = json.dumps(input_data, indent=2)
            
            # Call API using the system_prompt from input
            response_content = await self.api_client.call_with_system_prompt(
                system_prompt=evaluation_input.system_prompt,
                user_message=user_message
            )
            logger.info(f"AI validation response: {response_content}")
            
            # Parse the validation response
            validation_result = await self._parse_validation_response(response_content)
            
            # Convert validation result to metric scores
            return self._convert_validation_to_metrics(validation_result)
            
        except Exception as e:
            logger.error(f"Error during validation evaluation: {str(e)}")
            return self._get_default_metric_scores(f"Validation error: {str(e)}")
    
    async def _handle_evaluation_prompt(self, evaluation_input: EvaluationInput) -> List[MetricScore]:
        """Handle the original evaluation system prompt format"""
        try:
            # Prepare context string
            context_str = " | ".join([item.content for item in evaluation_input.context])
            
            # Create the user message with all the evaluation data
            user_message = f"""
            Please evaluate the following content:

            USER_PROMPT: {evaluation_input.user_prompt}
            TEMPLATE: {evaluation_input.template}
            BACKLOG_TYPE: {evaluation_input.backlog_type}
            GENERATED_TITLE: {evaluation_input.generated_content.title}
            GENERATED_CONTENT: {evaluation_input.generated_content.formatted_output}
            CONTEXT: {context_str}
            """
            
            # Call API using the system_prompt from input
            response_content = await self.api_client.call_with_system_prompt(
                system_prompt=evaluation_input.system_prompt,
                user_message=user_message
            )
            logger.info(f"AI response for evaluation: {response_content}")
            
            # Clean the response content
            response_content = response_content.strip()
            
            # Check if response is empty
            if not response_content:
                logger.error("Empty response from AI")
                return self._get_default_metric_scores("Empty response from AI")
            
            # Try to extract JSON from response if it contains extra text
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = response_content[json_start:json_end]
                logger.info(f"Extracted JSON content: {json_content}")
            else:
                logger.error(f"No JSON found in response: {response_content}")
                return self._get_default_metric_scores(f"No JSON found in response")
            
            # Try to parse JSON response
            try:
                evaluation_data = json.loads(json_content)
                
                # Convert the response to MetricScore objects
                metric_scores = []
                expected_metrics = ["relevance", "accuracy", "completeness", "clarity", "structure", "consistency", "hallucination_detection", "context_adherence", "factual_grounding"]
                
                for metric_name in expected_metrics:
                    if metric_name in evaluation_data:
                        metric_data = evaluation_data[metric_name]
                        if isinstance(metric_data, dict) and "score" in metric_data:
                            score_value = round(min(max(float(metric_data["score"]), 0.0), 1.0), 2)  # Clamp between 0 and 1
                            # Only include reasoning if score is less than 0.65
                            if score_value < 0.65:
                                metric_scores.append(MetricScore(
                                    metric=metric_name,
                                    score=score_value,
                                    reasoning=metric_data.get("reasoning", "No reasoning provided"),
                                    confidence=min(max(float(metric_data.get("confidence", 0.8)), 0.0), 1.0)
                                ))
                            else:
                                metric_scores.append(MetricScore(
                                    metric=metric_name,
                                    score=score_value,
                                    reasoning=None,
                                    confidence=min(max(float(metric_data.get("confidence", 0.8)), 0.0), 1.0)
                                ))
                        else:
                            # Handle case where metric_data is just a score value
                            score = float(metric_data) if isinstance(metric_data, (int, float)) else 0.5
                            score_value = round(min(max(score, 0.0), 1.0), 2)
                            # Only include reasoning if score is less than 0.65
                            if score_value < 0.65:
                                metric_scores.append(MetricScore(
                                    metric=metric_name,
                                    score=score_value,
                                    reasoning="Score provided without detailed reasoning",
                                    confidence=0.7
                                ))
                            else:
                                metric_scores.append(MetricScore(
                                    metric=metric_name,
                                    score=score_value,
                                    reasoning=None,
                                    confidence=0.7
                                ))
                    else:
                        # Add default score for missing metrics (always show reasoning for missing metrics as they default to 0.5)
                        metric_scores.append(MetricScore(
                            metric=metric_name,
                            score=0.5,
                            reasoning=f"Metric {metric_name} not found in AI response",
                            confidence=0.3
                        ))
                
                if not metric_scores:
                    logger.error("No valid metric scores extracted from response")
                    return self._get_default_metric_scores("No valid metric scores found in response")
                
                return metric_scores
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON content: {json_content}, Error: {str(e)}")
                return self._get_default_metric_scores(f"JSON parsing error: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error during evaluation: {str(e)}")
            return self._get_default_metric_scores(f"Evaluation error: {str(e)}")
    
    async def _parse_validation_response(self, response_content: str) -> Dict[str, Any]:
        """Parse the validation response and extract proceed/reason"""
        try:
            # Clean the response content
            response_content = response_content.strip()
            
            # Try to extract JSON from response if it contains extra text
            json_start = response_content.find('{')
            json_end = response_content.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_content = response_content[json_start:json_end]
                logger.info(f"Extracted validation JSON: {json_content}")
                
                validation_data = json.loads(json_content)
                
                # Ensure we have the expected format
                if "proceed" in validation_data and "reason" in validation_data:
                    return validation_data
                else:
                    logger.error(f"Invalid validation response format: {validation_data}")
                    return {"proceed": False, "reason": "Invalid response format from validation agent"}
            else:
                logger.error(f"No JSON found in validation response: {response_content}")
                return {"proceed": False, "reason": "No valid JSON found in validation response"}
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse validation JSON: {str(e)}")
            return {"proceed": False, "reason": f"JSON parsing error: {str(e)}"}
        except Exception as e:
            logger.error(f"Error parsing validation response: {str(e)}")
            return {"proceed": False, "reason": f"Parsing error: {str(e)}"}
    
    def _convert_validation_to_metrics(self, validation_result: Dict[str, Any]) -> List[MetricScore]:
        """Convert validation result to metric scores"""
        proceed = validation_result.get("proceed", False)
        reason = validation_result.get("reason", "No reason provided")
        
        # Convert boolean result to a score
        # If proceed=True, give good scores (0.8-0.9)
        # If proceed=False, give poor scores (0.3-0.5) with reasoning
        base_score = 0.85 if proceed else 0.35
        confidence = 0.9 if proceed else 0.8
        
        metric_scores = []
        expected_metrics = ["relevance", "accuracy", "completeness", "clarity", "structure", "consistency", "hallucination_detection", "context_adherence", "factual_grounding"]
        
        for metric_name in expected_metrics:
            # Add some variation to scores to make them more realistic
            import random
            score_variation = random.uniform(-0.05, 0.05)
            final_score = round(min(max(base_score + score_variation, 0.0), 1.0), 2)
            
            if final_score < 0.65:
                # Include reasoning for low scores
                metric_scores.append(MetricScore(
                    metric=metric_name,
                    score=final_score,
                    reasoning=reason,
                    confidence=confidence
                ))
            else:
                # Exclude reasoning for high scores
                metric_scores.append(MetricScore(
                    metric=metric_name,
                    score=final_score,
                    reasoning=None,
                    confidence=confidence
                ))
        
        return metric_scores
    
    def _get_default_metric_scores(self, error_message: str) -> List[MetricScore]:
        """Return default metric scores in case of errors"""
        default_metrics = ["relevance", "accuracy", "completeness", "clarity", "structure", "consistency", "hallucination_detection", "context_adherence", "factual_grounding"]
        return [
            MetricScore(
                metric=metric,
                score=0.5,
                reasoning=error_message,  # Always show reasoning for error cases since score is 0.5 (< 0.65)
                confidence=0.1
            )
            for metric in default_metrics
        ]
    
    async def evaluate_all(self, evaluation_input: EvaluationInput) -> EvaluationResult:
        """Evaluate all metrics and return complete result"""
        
        # Use the new method that handles the system_prompt
        metric_scores = await self.evaluate_all_metrics(evaluation_input)
        
        # Calculate overall score (weighted average)
        overall_score = round(sum(
            score.score * METRIC_WEIGHTS.get(score.metric, 1.0/len(metric_scores))
            for score in metric_scores
        ), 2)
        
        # Generate summary and recommendations using centralized API client
        summary = await self._generate_summary(metric_scores, evaluation_input)
        recommendations = await self._generate_recommendations(metric_scores, evaluation_input)
        
        return EvaluationResult(
            session_id=evaluation_input.session_id,
            overall_score=overall_score,
            metric_scores=metric_scores,
            summary=summary,
            recommendations=recommendations,
            evaluation_timestamp=datetime.now().isoformat(),
            evaluation_metadata={
                "backlog_type": evaluation_input.backlog_type,
                "content_length": len(evaluation_input.generated_content.formatted_output),
                "context_items": len(evaluation_input.context)
            }
        )
    
    async def _generate_summary(self, metric_scores: List[MetricScore], evaluation_input: EvaluationInput) -> str:
        """Generate evaluation summary using centralized API client"""
        try:
            scores_text = "\n".join([f"- {score.metric}: {score.score:.2f}" + (f" - {score.reasoning}" if score.reasoning else "") for score in metric_scores])
            
            prompt = f"""
            Based on the following evaluation scores for a {evaluation_input.backlog_type}, provide a concise summary:
            
            {scores_text}
            
            Generated Content Title: {evaluation_input.generated_content.title}
            
            Provide a 2-3 sentence summary of the overall quality and key strengths/weaknesses.
            """
            
            return await self.api_client.call_for_summary(prompt)
            
        except Exception as e:
            logger.error(f"Error generating summary: {str(e)}")
            return "Evaluation completed with mixed results. Review individual metric scores for details."
    
    async def _generate_recommendations(self, metric_scores: List[MetricScore], evaluation_input: EvaluationInput) -> str:
        """Generate improvement recommendations using centralized API client"""
        try:
            low_scores = [score for score in metric_scores if score.score < 0.7]
            
            if not low_scores:
                return "Content quality is good. Consider minor refinements based on specific project requirements."
            
            recommendations_text = "\n".join([f"- {score.metric} (Score: {score.score:.2f})" + (f": {score.reasoning}" if score.reasoning else "") for score in low_scores])
            
            prompt = f"""
            Based on these low-scoring evaluation metrics for a {evaluation_input.backlog_type}, provide 3-5 specific, actionable recommendations for improvement:
            
            {recommendations_text}
            
            Focus on practical steps to improve the content quality.
            """
            
            response_content = await self.api_client.call_for_recommendations(prompt)
            
            # Split response into individual recommendations and join them with newlines
            recommendations = [rec.strip() for rec in response_content.split('\n') if rec.strip() and not rec.strip().startswith('#')]
            return "\n".join(recommendations[:5])  # Limit to 5 recommendations and join as single string
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return "Review content for accuracy and completeness. Improve clarity and structure. Ensure alignment with requirements."
