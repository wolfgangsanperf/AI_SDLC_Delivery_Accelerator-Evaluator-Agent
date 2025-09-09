# Response Evaluator Agent API

A FastAPI-based service that evaluates generated content using LLM-as-a-judge methodology. This API provides comprehensive quality assessment across multiple evaluation metrics, making it ideal for assessing AI-generated software development artifacts like user stories, requirements, and backlog items.

## 🚀 Features

- **Multi-Metric Evaluation**: Comprehensive assessment across 9 quality dimensions
- **LLM-as-a-Judge**: Leverages advanced AI models for intelligent content evaluation
- **DeepEval Integration**: Built-in support for industry-standard evaluation metrics
- **Async Processing**: High-performance async evaluation with concurrent metric processing
- **Retry Logic**: Robust error handling with exponential backoff
- **Detailed Feedback**: Actionable recommendations for content improvement
- **REST API**: Clean, well-documented API endpoints with OpenAPI/Swagger support

## 📊 Evaluation Metrics

The API evaluates content across nine comprehensive quality dimensions with optimized weighted scoring:

| Metric | Weight | Description |
|--------|--------|-------------|
| **Relevance** | 18% | How well the content addresses the user's prompt |
| **Accuracy** | 15% | Factual correctness and technical accuracy |
| **Completeness** | 15% | Whether all necessary sections are included |
| **Hallucination Detection** | 12% | Identifies and penalizes fabricated or unsupported claims |
| **Clarity** | 12% | Readability and professional language |
| **Structure** | 8% | Proper formatting and organization |
| **Consistency** | 8% | Internal consistency and alignment with context |
| **Context Adherence** | 8% | Alignment with provided contextual information |
| **Factual Grounding** | 4% | Verification of claims against reliable sources |

### Scoring Scale
- **Excellent**: > 0.8
- **Good**: 0.7 - 0.8
- **Needs Improvement**: < 0.7

### Advanced Features

**Intelligent Reasoning System**
The API implements intelligent reasoning inclusion based on score thresholds:
- **Scores ≥ 0.65**: The `reasoning` field is **excluded** from the response to keep high-performing metrics clean
- **Scores < 0.65**: The `reasoning` field is **included** with detailed explanations for improvement areas

**Dual Evaluation Modes**
- **Validation Mode**: Binary proceed/reason format for template compliance checking
- **Comprehensive Mode**: Full multi-metric evaluation with detailed scoring

**Enhanced Security**
- **Hallucination Detection**: Advanced detection of fabricated content (threshold: 0.8)
- **Context Adherence**: Similarity validation against provided context (threshold: 0.7)
- **Factual Grounding**: Confidence verification for factual claims (threshold: 0.6)

## 🏗️ Architecture

The project follows a modular architecture with clear separation of concerns:

```
src/
├── main.py          # FastAPI application and endpoints
├── models.py        # Pydantic models and data structures
├── config.py        # Configuration settings and constants
├── clients.py       # External API clients (Portkey)
├── evaluators.py    # Core evaluation logic
├── prompts.py       # LLM prompts for different metrics
└── __init__.py      # Package initialization
```

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **DeepEval**: Evaluation framework for LLM applications
- **Portkey AI**: LLM gateway for API management and routing
- **LangChain**: Framework for developing LLM applications
- **Uvicorn**: ASGI server for production deployment
- **Poetry**: Dependency management and packaging

## 📋 Prerequisites

- **Python**: 3.13.7 (verified compatible with 3.12.3+)
- **Poetry**: For dependency management and virtual environment
- **Podman/Docker**: For containerized services (optional)
- **Environment**: Linux/WSL compatible (Ubuntu 24.04+ recommended)

## 🚀 Quick Start

### 1. Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd my-awesome-api

# Install dependencies
poetry install
poetry shell
```

### 2. Environment Configuration

Create a `.env` file in the `src/` directory:

```bash
# Portkey AI Configuration
PORTKEY_API_KEY=your_portkey_api_key_here
PORTKEY_BASE_URL=https://your-portkey-gateway-url.com/v1

# Optional: Application Configuration
LOG_LEVEL=INFO
DEBUG=False
```

### 3. Start Infrastructure Services (Optional)

If you need the full development environment with databases:

```bash
cd local-infrastructure
podman-compose -f python-dev-compose.yml up -d
```

### 4. Run the Application

```bash
# Development mode with auto-reload
poetry run python src/main.py

# Or using uvicorn directly
poetry run uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 📖 API Usage

### Evaluate Content

**POST** `/evaluate`

```json
{
  "session_id": "unique-session-id",
  "backlog_type": "user_story",
  "user_prompt": "Create a user story for login functionality",
  "generated_content": {
    "title": "User Login Story",
    "formatted_output": "## User Story\nAs a user, I want to log in..."
  },
  "context": [
    {
      "content": "Authentication requirements: OAuth2, multi-factor auth"
    }
  ]
}
```

**Response:**
```json
{
  "status": 200,
  "timestamp": "2025-01-09T21:35:00",
  "message": "Evaluation completed successfully",
  "body": {
    "session_id": "unique-session-id",
    "backlog_type": "user_story",
    "status": "completed",
    "evaluation_metrics": {
      "overall_score": 0.82,
      "metric_scores": [
        {
          "metric": "relevance",
          "score": 0.92,
          "confidence": 0.95
        },
        {
          "metric": "accuracy",
          "score": 0.88,
          "confidence": 0.90
        },
        {
          "metric": "completeness",
          "score": 0.45,
          "reasoning": "Missing acceptance criteria and edge case handling",
          "confidence": 0.85
        },
        {
          "metric": "clarity",
          "score": 0.90,
          "confidence": 0.92
        },
        {
          "metric": "hallucination_detection",
          "score": 0.95,
          "confidence": 0.88
        },
        {
          "metric": "context_adherence",
          "score": 0.87,
          "confidence": 0.91
        },
        {
          "metric": "factual_grounding",
          "score": 0.79,
          "confidence": 0.84
        }
      ],
      "summary": "High-quality user story with excellent relevance and minimal hallucination risk. Requires enhanced acceptance criteria for completeness.",
      "recommendations": "Add specific acceptance criteria with measurable outcomes" 
    },
    "evaluation_metadata": {
      "tokens_used": 180,
      "tokens_generated": 95,
      "evaluation_time_ms": 1150,
      "model_version": "gpt-4o-mini",
      "evaluation_mode": "comprehensive"
    }
  }
}
```

**Note**: In the example above, notice that:
- High scores (≥ 0.65) like `relevance`, `accuracy`, and `clarity` have **no reasoning field**
- Low scores (< 0.65) like `completeness` **include the reasoning field** with detailed explanations

### Health Check

**GET** `/health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2025-01-06T15:30:00",
  "service": "Response Evaluator Agent"
}
```

### Metrics Information

**GET** `/metrics/info`

Returns detailed information about available evaluation metrics and their weights.

## 🔧 Configuration

Key configuration options in `src/config.py` (Latest Version):

```python
# API Configuration
API_TITLE = "Response Evaluator Agent"
API_VERSION = "1.0.0"
HOST = "0.0.0.0"
PORT = 8000

# Model Configuration
PORTKEY_MODEL = "gpt-4o-mini"
PORTKEY_PROVIDER = "@azure-openai"
DEFAULT_TEMPERATURE = 0.6
MAX_TOKENS_GENERATION = 2000
MAX_TOKENS_SUMMARY = 200
MAX_TOKENS_RECOMMENDATIONS = 300

# Performance Configuration
MAX_RETRIES = 3
RETRY_DELAY = 1.0

# Updated Evaluation Weights (9 Metrics)
METRIC_WEIGHTS = {
    "relevance": 0.18,
    "accuracy": 0.15,
    "completeness": 0.15,
    "hallucination_detection": 0.12,
    "clarity": 0.12,
    "structure": 0.08,
    "consistency": 0.08,
    "context_adherence": 0.08,
    "factual_grounding": 0.04
}

# Security & Quality Thresholds
HALLUCINATION_THRESHOLD = 0.8          # Minimum score to pass hallucination detection
CONTEXT_SIMILARITY_THRESHOLD = 0.7     # Minimum similarity to provided context
FACTUAL_CONFIDENCE_THRESHOLD = 0.6     # Minimum confidence for factual claims
DEEPEVAL_THRESHOLD = 0.7               # Pass/fail threshold for DeepEval metrics
```

### Threshold Explanations

**HALLUCINATION_THRESHOLD (0.8)**
- **Purpose**: Detects fabricated or unsupported claims in generated content
- **How it works**: Content scoring below 0.8 is flagged as potentially containing hallucinations
- **Impact**: Higher threshold = stricter hallucination detection, more conservative evaluation

**CONTEXT_SIMILARITY_THRESHOLD (0.7)**  
- **Purpose**: Ensures generated content aligns with provided contextual information
- **How it works**: Measures semantic similarity between generated content and input context
- **Impact**: Content must be at least 70% similar to context to pass adherence checks

**FACTUAL_CONFIDENCE_THRESHOLD (0.6)**
- **Purpose**: Validates confidence level of factual claims made in the content
- **How it works**: AI model's confidence in factual statements must exceed 60%
- **Impact**: Low-confidence facts trigger reasoning explanations and lower scores

**DEEPEVAL_THRESHOLD (0.7)**
- **Purpose**: Binary pass/fail criterion for DeepEval framework metrics
- **How it works**: Metrics scoring above 0.7 are considered "passing" quality
- **Impact**: Used for quick quality gates and automated decision making

## 🐳 Infrastructure Services

The project includes containerized development services:

### Services Included
- **PostgreSQL** (port 5432): Database with pgvector extension
- **Redis** (port 6379): Caching and session management
- **n8n** (port 5678): Workflow automation platform

### Service URLs
- **n8n Workflow Editor**: http://localhost:5678
  - Username: `sdlc_user`
  - Password: `sdlc_password`

### Podman Commands

```bash
cd local-infrastructure

# Start all services
podman-compose -f python-dev-compose.yml up -d

# Stop all services
podman-compose -f python-dev-compose.yml down

# View logs
podman logs python-dev-postgres
podman logs python-dev-redis
podman logs python-dev-n8n
```

## 🧪 Development

### Code Structure

The codebase follows Python best practices with:
- **Type hints** throughout
- **Docstrings** for all public functions
- **Async/await** for I/O operations
- **Error handling** with proper logging
- **Modular design** for maintainability

### Adding New Metrics

To add a new evaluation metric:

1. Add the metric to `EvaluationMetric` enum in `models.py`
2. Create a prompt template in `prompts.py`
3. Add the metric weight in `config.py`
4. Update the evaluator logic in `evaluators.py`

### Running Tests

```bash
# Install dev dependencies
poetry install --with dev

# Run tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=src
```

### Code Quality

```bash
# Format code
poetry run black src/

# Sort imports
poetry run isort src/

# Lint code
poetry run flake8 src/

# Type checking
poetry run mypy src/
```

## 📦 Deployment

### Production Configuration

For production deployment:

1. Set environment variables:
   ```bash
   export PORTKEY_API_KEY=your_production_key
   export PORTKEY_BASE_URL=your_production_url
   export LOG_LEVEL=WARNING
   ```

2. Use a production ASGI server:
   ```bash
   poetry run gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Docker Deployment

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install --only=main

COPY src/ ./src/
EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Monitoring and Logging

The application provides comprehensive logging:

- **File logging**: `evaluation_results.log`
- **Console logging**: Structured JSON logs
- **Request tracking**: Unique request IDs
- **Performance metrics**: Evaluation timing
- **Error tracking**: Detailed error context

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code style
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📄 License

This project is part of the SDLC AI Delivery Accelerator framework.

## 🆘 Troubleshooting

### Common Issues

**API Connection Issues**
- Verify `PORTKEY_API_KEY` and `PORTKEY_BASE_URL` are set correctly
- Check network connectivity to the Portkey gateway
- Review logs for specific error messages

**Dependencies Issues**
- Ensure Python 3.13.7+ is installed
- Run `poetry install` to update dependencies
- Use `poetry shell` to activate the virtual environment

**Database Connection Issues**
- Ensure infrastructure services are running: `podman-compose ps`
- Check logs: `podman logs python-dev-postgres`
- Verify port availability (5432, 6379, 5678)

### Getting Help

- Check the application logs in `evaluation_results.log`
- Review the API documentation at `/docs`
- Examine the health check endpoint at `/health`

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [DeepEval Documentation](https://docs.deepeval.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Poetry Documentation](https://python-poetry.org/docs/)
