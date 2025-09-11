"""
Evaluation prompts for different metrics used by the Response Evaluator Agent.
"""
from src.api.backlog_evaluator_contracts import EvaluationMetric


EVALUATION_PROMPTS = {
    EvaluationMetric.RELEVANCE: """
    Evaluate how well the generated content addresses the user's prompt and follows the provided template.
    
    User Prompt: {user_prompt}
    Template Instructions: {template}
    Generated Title: {title}
    Generated Content: {content}
    Context: {context}
    
    Consider:
    - Does the generated content directly address what the user asked for?
    - Is the title appropriate for the content?
    - Does it match the requested backlog type ({backlog_type})?
    - Does it follow the format and structure specified in the template?
    
    Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """,
    
    EvaluationMetric.ACCURACY: """
    Evaluate the factual accuracy and technical correctness of the generated content.
    
    Generated Content: {content}
    Context: {context}
    Backlog Type: {backlog_type}
    
    Consider:
    - Are the technical details correct?
    - Are the acceptance criteria realistic and testable?
    - Are the non-functional requirements properly specified?
    - Is the content consistent with the provided context?
    
    Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """,
    
    EvaluationMetric.COMPLETENESS: """
    Evaluate how complete the generated content is for the requested backlog type and template requirements.
    
    User Prompt: {user_prompt}
    Template Instructions: {template}
    Generated Content: {content}
    Backlog Type: {backlog_type}
    
    Consider:
    - Does it include all necessary sections for a {backlog_type}?
    - Does it include all sections and elements specified in the template?
    - Are acceptance criteria comprehensive?
    - Are non-functional requirements included where appropriate?
    - Is anything important missing from the template requirements?
    
    Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """,
    
    EvaluationMetric.CLARITY: """
    Evaluate the clarity and readability of the generated content.
    
    Generated Content: {content}
    
    Consider:
    - Is the language clear and professional?
    - Are the requirements easy to understand?
    - Is the structure logical and well-organized?
    - Would stakeholders easily understand this content?
    
    Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """,
    
    EvaluationMetric.STRUCTURE: """
    Evaluate the structure and format of the generated content against template requirements.
    
    Template Instructions: {template}
    Generated Content: {content}
    Backlog Type: {backlog_type}
    
    Consider:
    - Is the markdown formatting correct and consistent?
    - Are sections properly organized according to the template?
    - Does it follow the structure specified in the template?
    - Does it follow standard {backlog_type} format conventions?
    - Is the hierarchy clear (headers, subheaders, etc.)?
    
    Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """,
    
    EvaluationMetric.CONSISTENCY: """
    Evaluate the consistency within the generated content and with the context.
    
    Generated Content: {content}
    Context: {context}
    User Prompt: {user_prompt}
    
    Consider:
    - Is the content internally consistent?
    - Does it align with the provided context?
    - Are there any contradictions or inconsistencies?
    - Is the tone and style consistent throughout?
    
    Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """,
    
    EvaluationMetric.HALLUCINATION_DETECTION: """
    Evaluate whether the generated content contains hallucinated information that is not supported by the provided context.
    
    Generated Content: {content}
    Context: {context}
    User Prompt: {user_prompt}
    
    Consider:
    - Does the content make claims not supported by the context?
    - Are there any fabricated technical details, requirements, or specifications?
    - Does the content introduce information not present in the source context?
    - Are all factual statements verifiable against the provided context?
    
    Rate from 0.0 (high hallucination) to 1.0 (no hallucination) and explain your reasoning.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """,
    
    EvaluationMetric.CONTEXT_ADHERENCE: """
    Evaluate how well the generated content adheres to and stays grounded in the provided context.
    
    Generated Content: {content}
    Context: {context}
    Backlog Type: {backlog_type}
    
    Consider:
    - Does the content strictly follow information from the context?
    - Are all requirements and specifications derived from the context?
    - Does it avoid introducing external assumptions or knowledge?
    - How well does it maintain fidelity to the source material?
    
    Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """,
    
    EvaluationMetric.FACTUAL_GROUNDING: """
    Evaluate the factual grounding and verifiability of claims made in the generated content.
    
    Generated Content: {content}
    Context: {context}
    Backlog Type: {backlog_type}
    
    Consider:
    - Are technical specifications and requirements factually grounded?
    - Can all claims be traced back to the provided context?
    - Are acceptance criteria realistic and implementable?
    - Does the content avoid speculative or unverifiable statements?
    
    Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum.
    
    Respond in JSON format:
    {{
        "score": <float>,
        "reasoning": "<brief 1-2 sentence explanation>",
        "confidence": <float>
    }}
    """
}


# System prompts for different API calls
SYSTEM_PROMPTS = {
    "evaluation": "You are an expert evaluator of software development artifacts. Provide precise, objective evaluations.",
    "summary": "You are an expert at summarizing evaluation results.",
    "recommendations": "You are an expert at providing actionable improvement recommendations."
}


# System prompts for POST request JSON schema
REQUEST_SYSTEM_PROMPTS = {
    "relevance": "You are an expert evaluator of software development artifacts. Provide precise, objective evaluations. Evaluate how well the generated content addresses the user's prompt and follows the provided template. Consider: Does the generated content directly address what the user asked for? Is the title appropriate for the content? Does it match the requested backlog type? Does it follow the format and structure specified in the template? Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum. Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "accuracy": "You are an expert evaluator of software development artifacts. Provide precise, objective evaluations. Evaluate the factual accuracy and technical correctness of the generated content. Consider: Are the technical details correct? Are the acceptance criteria realistic and testable? Are the non-functional requirements properly specified? Is the content consistent with the provided context? Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum. Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "completeness": "You are an expert evaluator of software development artifacts. Provide precise, objective evaluations. Evaluate how complete the generated content is for the requested backlog type and template requirements. Consider: Does it include all necessary sections for the specified backlog type? Does it include all sections and elements specified in the template? Are acceptance criteria comprehensive? Are non-functional requirements included where appropriate? Is anything important missing from the template requirements? Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum. Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "clarity": "You are an expert evaluator of software development artifacts. Provide precise, objective evaluations. Evaluate the clarity and readability of the generated content. Consider: Is the language clear and professional? Are the requirements easy to understand? Is the structure logical and well-organized? Would stakeholders easily understand this content? Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum. Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "structure": "You are an expert evaluator of software development artifacts. Provide precise, objective evaluations. Evaluate the structure and format of the generated content against template requirements. Consider: Is the markdown formatting correct and consistent? Are sections properly organized according to the template? Does it follow the structure specified in the template? Does it follow standard format conventions for the specified backlog type? Is the hierarchy clear (headers, subheaders, etc.)? Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum. Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "consistency": "You are an expert evaluator of software development artifacts. Provide precise, objective evaluations. Evaluate the consistency within the generated content and with the context. Consider: Is the content internally consistent? Does it align with the provided context? Are there any contradictions or inconsistencies? Is the tone and style consistent throughout? Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum. Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "hallucination_detection": "You are an expert evaluator of software development artifacts specializing in hallucination detection. Provide precise, objective evaluations. Evaluate whether the generated content contains hallucinated information not supported by the provided context. Consider: Does the content make claims not supported by the context? Are there fabricated technical details, requirements, or specifications? Does the content introduce information not present in the source context? Are all factual statements verifiable against the provided context? Rate from 0.0 (high hallucination) to 1.0 (no hallucination). Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "context_adherence": "You are an expert evaluator of software development artifacts specializing in context adherence. Provide precise, objective evaluations. Evaluate how well the generated content adheres to and stays grounded in the provided context. Consider: Does the content strictly follow information from the context? Are all requirements and specifications derived from the context? Does it avoid introducing external assumptions or knowledge? How well does it maintain fidelity to the source material? Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum. Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "factual_grounding": "You are an expert evaluator of software development artifacts specializing in factual grounding assessment. Provide precise, objective evaluations. Evaluate the factual grounding and verifiability of claims made in the generated content. Consider: Are technical specifications and requirements factually grounded? Can all claims be traced back to the provided context? Are acceptance criteria realistic and implementable? Does the content avoid speculative or unverifiable statements? Rate from 0.0 to 1.0 and explain your reasoning in 1-2 sentences maximum. Respond in JSON format: {\"score\": <float>, \"reasoning\": \"<brief 1-2 sentence explanation>\", \"confidence\": <float>}",
    
    "summary": "You are an expert at summarizing evaluation results. Provide a comprehensive summary of the evaluation metrics and overall assessment of the generated content quality.",
    
    "recommendations": "You are an expert at providing actionable improvement recommendations. Analyze the evaluation results and provide specific, actionable suggestions for improving the generated content."
}
