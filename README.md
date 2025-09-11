# AI SDLC Delivery Accelerator - Evaluator Agent

A sophisticated FastAPI-based microservice that evaluates AI-generated software development artifacts (user stories, epics, requirements) using **LLM-as-a-judge methodology**. This service provides comprehensive quality assessment across multiple evaluation metrics, ensuring generated content meets professional standards.

## 🚀 Features

- **Multi-Metric Evaluation**: Comprehensive assessment across 9 quality dimensions
- **LLM-as-a-Judge**: Leverages advanced AI models for intelligent content evaluation
- **DeepEval Integration**: Built-in support for industry-standard evaluation metrics
- **Async Processing**: High-performance async evaluation with concurrent metric processing
- **Retry Logic**: Robust error handling with exponential backoff
- **Detailed Feedback**: Actionable recommendations for content improvement
- **REST API**: Clean, well-documented API endpoints with OpenAPI/Swagger support
- **Standardized Configuration**: Environment-driven configuration following microservice patterns
- **Comprehensive Logging**: Structured logging with file and console output

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

## 🏗️ Architecture

The project follows a clean architecture with clear separation of concerns:

```
src/
├── main.py                           # FastAPI application entry point
├── api/                             # API layer
│   ├── backlog_evaluator_api.py     # API controllers/routes
│   └── backlog_evaluator_contracts.py # Pydantic models
├── service/                         # Business logic layer
│   ├── evaluation_service.py        # Core evaluation business logic
│   ├── evaluators.py               # DeepEval evaluation engine
│   ├── clients.py                  # External API clients
│   └── prompts.py                  # LLM prompt templates
├── config/                         # Configuration layer
│   └── config.py                   # Standardized configuration
└── utils/                          # Utility functions
```

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **DeepEval**: Evaluation framework for LLM applications
- **Portkey AI**: LLM gateway for API management and routing
- **Uvicorn**: ASGI server for production deployment
- **Poetry**: Dependency management and packaging

## 📋 Prerequisites

- **Python**: 3.12+ (verified compatible with 3.13)
- **Poetry**: For dependency management and virtual environment
- **Portkey Account**: For LLM API access
- **Environment**: Linux/WSL/macOS compatible

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd AI_SDLC_Delivery_Accelerator-Evaluator-Agent
```

### 2. Install Dependencies

```bash
# Install Poetry if you haven't already
pip install poetry

# Install project dependencies
poetry install

# Activate virtual environment
poetry shell
```

### 3. Environment Configuration

Create your environment configuration file:

```bash
# Copy the example environment file
cp .env.example .env

# Edit the .env file with your configuration
nano .env  # or use your preferred editor
```

### 4. Configure Environment Variables

Edit the `.env` file with your specific configuration:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8010
API_RELOAD=true
LOG_LEVEL=info

# LLM Provider Configuration (Required)
PORTKEY_BASE_URL=https://your-portkey-gateway.com/v1
PORTKEY_API_KEY=your_actual_portkey_api_key
PORTKEY_MODEL=gpt-4o-mini
PORTKEY_PROVIDER=@azure-openai

# Application Behavior (Optional - defaults provided)
DEFAULT_TEMPERATURE=0.6
MAX_TOKENS_GENERATION=2000

# Evaluation Thresholds (Optional - defaults provided)
DEEPEVAL_THRESHOLD=0.7
HALLUCINATION_THRESHOLD=0.8

# Logging Configuration (Optional)
LOG_FILE=evaluation_results.log
CONSOLE_LOGGING=true
```

### 5. Start the Application

```bash
# Development mode with auto-reload
python -m src.main

# Or using uvicorn directly
uvicorn src.main:app --host 0.0.0.0 --port 8010 --reload
```

The API will be available at:
- **API**: http://localhost:8010
- **Interactive Docs**: http://localhost:8010/docs
- **ReDoc**: http://localhost:8010/redoc

## 🔧 Configuration Reference

### Environment Variables

#### API Configuration
- `API_HOST` - Server host (default: 0.0.0.0)
- `API_PORT` - Server port (default: 8010)
- `API_RELOAD` - Enable auto-reload in development (default: true)
- `LOG_LEVEL` - Logging level (default: info)

#### LLM Provider Configuration (Required)
- `PORTKEY_BASE_URL` - Portkey gateway URL (**Required**)
- `PORTKEY_API_KEY` - Portkey API key (**Required**)
- `PORTKEY_MODEL` - LLM model to use (default: gpt-4o-mini)
- `PORTKEY_PROVIDER` - LLM provider (default: @azure-openai)

#### Application Behavior
- `DEFAULT_TEMPERATURE` - LLM temperature (default: 0.6)
- `MAX_TOKENS_GENERATION` - Max tokens for generation (default: 2000)
- `MAX_TOKENS_SUMMARY` - Max tokens for summary (default: 200)
- `MAX_TOKENS_RECOMMENDATIONS` - Max tokens for recommendations (default: 300)

#### Retry Configuration
- `MAX_RETRIES` - Maximum retry attempts (default: 3)
- `RETRY_DELAY` - Base retry delay in seconds (default: 1.0)
- `EXPONENTIAL_BACKOFF` - Enable exponential backoff (default: true)

#### Evaluation Configuration
- `DEEPEVAL_THRESHOLD` - Pass/fail threshold for DeepEval metrics (default: 0.7)
- `HALLUCINATION_THRESHOLD` - Minimum score for hallucination detection (default: 0.8)
- `CONTEXT_SIMILARITY_THRESHOLD` - Minimum similarity to context (default: 0.7)
- `FACTUAL_CONFIDENCE_THRESHOLD` - Minimum confidence for facts (default: 0.6)

#### Logging Configuration
- `LOG_FILE` - Log file name (default: evaluation_results.log)
- `CONSOLE_LOGGING` - Enable console logging (default: true)

## 📖 API Usage

### Health Check

Check if the service is running and healthy:

```bash
curl -X GET http://localhost:8010/validate/health
```

**Response:**
```json
{
  "status": 200,
  "timestamp": "2025-01-09T21:35:00",
  "message": "Health check passed successfully",
  "body": {
    "status": "healthy",
    "generator_model": {
      "name": "gpt-4o-mini",
      "status": "loaded"
    }
  }
}
```

### Evaluate Content

Evaluate generated SDLC content:

```bash
curl -X POST http://localhost:8010/validate/backlog-item-generated \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "unique-session-id",
    "backlog_type": "epic",
    "user_prompt": "Create an epic for improving mobile app onboarding",
    "system_prompt": "You are an expert evaluator...",
    "template": "Create a comprehensive epic with...",
    "generated_content": {
      "title": "Mobile App Onboarding Enhancement",
      "formatted_output": "## Epic: Mobile App Onboarding..."
    },
    "context": [
      {
        "content": "Current onboarding takes 15 minutes with 65% drop-off rate"
      }
    ]
  }'
```

### Get Metrics Information

Get information about evaluation metrics:

```bash
curl -X GET http://localhost:8010/metrics/info
```

## 🧪 Testing

### Quick Health Test

```bash
# Test basic connectivity
curl -f http://localhost:8010/validate/health || echo "Service not responding"
```

### Integration Test

Use the provided test request file:

```bash
# Test with sample evaluation request
curl -X POST http://localhost:8010/validate/backlog-item-generated \
  -H "Content-Type: application/json" \
  -d @request_test/corrected_evaluation_request.json
```

### Load Testing with curl

```bash
# Simple load test
for i in {1..10}; do
  curl -s -o /dev/null -w "%{http_code}\n" http://localhost:8010/validate/health
done
```

### Configuration Test

Verify environment variables are loaded correctly:

```bash
python -c "
from src.config.config import config
print(f'API Port: {config.api.port}')
print(f'LLM Model: {config.provider.llm_model}')
print('Configuration loaded successfully!')
"
```

## 🐳 Infrastructure Services (Optional)

The project includes containerized development services for advanced features:

### Services Included
- **PostgreSQL** (port 5432): Database with pgvector extension
- **Redis** (port 6379): Caching and session management
- **n8n** (port 5678): Workflow automation platform

### Start Infrastructure

```bash
cd local-infrastructure

# Start all services
podman-compose -f python-dev-compose.yml up -d

# Or with Docker
docker-compose -f python-dev-compose.yml up -d

# Stop services
podman-compose -f python-dev-compose.yml down
```

### Access Services
- **n8n Workflow Editor**: http://localhost:5678
  - Username: `sdlc_user`
  - Password: `sdlc_password`

## 📊 Monitoring and Logging

### Log Files

The application generates structured logs:

- **File**: `evaluation_results.log` (configurable via `LOG_FILE`)
- **Console**: Real-time logging (configurable via `CONSOLE_LOGGING`)
- **Format**: `timestamp - logger_name - level - message`

### Log Levels

Set via `LOG_LEVEL` environment variable:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages
- `ERROR`: Error messages only

### Monitoring Endpoints

- **Health Check**: `GET /validate/health`
- **Metrics Info**: `GET /metrics/info`
- **API Documentation**: `GET /docs`

## 🔍 Troubleshooting

### Common Issues

#### 1. Service Won't Start

**Problem**: Application fails to start
```bash
# Check configuration
python -c "from src.config.config import config; print('Config loaded')"

# Check port availability
lsof -i :8010

# Check logs
tail -f evaluation_results.log
```

#### 2. API Connection Issues

**Problem**: API calls fail or timeout
```bash
# Verify service is running
curl -f http://localhost:8010/validate/health

# Check Portkey configuration
echo "PORTKEY_API_KEY: $PORTKEY_API_KEY"
echo "PORTKEY_BASE_URL: $PORTKEY_BASE_URL"
```

#### 3. Environment Variables Not Loading

**Problem**: Configuration using defaults instead of .env values
```bash
# Verify .env file exists and is readable
ls -la .env
cat .env

# Test environment loading
python -c "import os; print(f'API_PORT: {os.getenv(\"API_PORT\", \"Not set\")}')"
```

#### 4. Import Errors

**Problem**: Python import errors
```bash
# Ensure virtual environment is activated
poetry shell

# Reinstall dependencies
poetry install --no-cache

# Check Python path
python -c "import sys; print('\n'.join(sys.path))"
```

#### 5. Logging Issues

**Problem**: Logs not appearing or log file not created
```bash
# Check log file permissions
touch evaluation_results.log
ls -la evaluation_results.log

# Test logging directly
python -c "
from src.config.config import logger
logger.info('Test log message')
print('Log test completed')
"
```

### Performance Issues

- **High Memory Usage**: Reduce `MAX_TOKENS_GENERATION`
- **Slow Responses**: Check network connectivity to Portkey gateway
- **Rate Limiting**: Adjust `RETRY_DELAY` and `MAX_RETRIES`

### Getting Help

1. **Check Logs**: Always check `evaluation_results.log` for detailed error information
2. **Verify Configuration**: Ensure all required environment variables are set
3. **Test Components**: Use the testing commands above to isolate issues
4. **API Documentation**: Visit `/docs` endpoint for interactive API testing

## 🤝 Development

### Project Structure

The project follows clean architecture principles:

- **API Layer**: Handles HTTP requests/responses
- **Service Layer**: Contains business logic
- **Configuration**: Environment-driven settings
- **Contracts**: Data models and validation

### Adding New Features

1. **New API Endpoints**: Add to `src/api/backlog_evaluator_api.py`
2. **Business Logic**: Add to `src/service/evaluation_service.py`
3. **Configuration**: Add environment variables to config dataclasses
4. **Models**: Add Pydantic models to `src/api/backlog_evaluator_contracts.py`

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

## 📄 License

This project is part of the SDLC AI Delivery Accelerator framework.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review logs in `evaluation_results.log`
3. Verify configuration with the testing commands
4. Contact the development team with specific error messages and configuration details
