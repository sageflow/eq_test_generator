# EQ Test Generator

A Python REST API application that generates ability-based emotional intelligence (EQ) tests for students aged 12-18. The API supports two providers for test generation:

1. **Ollama** - Local DeepSeek model running via Ollama
2. **DeepSeek Cloud API** - Official DeepSeek Cloud API

The test is generated section-by-section (4 branches) to avoid token limits and follows the Mayer-Salovey-Caruso Emotional Intelligence Test (MSCEIT) model.

## Features

- REST API endpoints for generating and managing EQ tests
- Section-by-section generation (4 branches) for better reliability
- Age-appropriate test generation for students aged 12-18
- Dual provider support (Ollama and DeepSeek Cloud API)
- Based on the Mayer-Salovey-Caruso Emotional Intelligence Test (MSCEIT) model
- Test storage with file-based persistence
- Automatic cleanup of old tests
- Asynchronous test generation with progress tracking

## Prerequisites

- Python 3.8+
- Ollama installed and running locally (if using Ollama provider)
- deepseek:7b model installed in Ollama (if using Ollama provider)
- DeepSeek Cloud API key (if using DeepSeek Cloud API provider)

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. **For Ollama provider:**
   - Ensure Ollama is running:
   ```bash
   ollama serve
   ```
   - Install the deepseek:7b model (if not already installed):
   ```bash
   ollama pull deepseek:7b
   ```

3. **For DeepSeek Cloud API provider:**
   - Get your API key from [DeepSeek Platform](https://platform.deepseek.com/)
   - Add it to your `.env` file (see Configuration section)

## Usage

1. Start the API server:
```bash
python app.py
```

Or using Flask directly:
```bash
flask run
```

2. The API will be available at `http://localhost:5000` (default)

3. Generate an EQ test by making a POST request:

```bash
# Using Ollama (default)
curl -X POST "http://localhost:5000/generate" \
     -H "Content-Type: application/json" \
     -d '{"age": 15}'

# Using DeepSeek Cloud API
curl -X POST "http://localhost:5000/generate" \
     -H "Content-Type: application/json" \
     -d '{"age": 15, "provider": "deepseek"}'
```

## API Endpoints

### Base URL

```
http://localhost:5000
```

### Authentication

No authentication is required for the API endpoints.

---

### 1. Health Check

Check if the API is running.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

**Example:**
```bash
curl "http://localhost:5000/health"
```

---

### 2. Generate EQ Test

Generate a new EQ test for a student of the specified age. The generation happens asynchronously in sections.

**Endpoint:** `POST /generate` or `POST /create-eq-test`

**Request Body:**
```json
{
  "age": 15,
  "provider": "ollama"
}
```

**Parameters:**
- `age` (integer, required): Student age between 12 and 18
- `provider` (string, optional): Either `"ollama"` or `"deepseek"`. Defaults to the `PROVIDER` environment variable (default: `"ollama"`)

**Response (Success):**
```json
{
  "success": true,
  "test_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "generating",
  "provider": "ollama",
  "message": "Test generation started"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Age must be between 12 and 18"
}
```

**Example using cURL:**
```bash
# Using Ollama (default)
curl -X POST "http://localhost:5000/generate" \
     -H "Content-Type: application/json" \
     -d '{"age": 15}'

# Using DeepSeek Cloud API
curl -X POST "http://localhost:5000/generate" \
     -H "Content-Type: application/json" \
     -d '{"age": 15, "provider": "deepseek"}'
```

**Example using Python:**
```python
import requests

# Using Ollama
response = requests.post(
    "http://localhost:5000/generate",
    json={"age": 15, "provider": "ollama"}
)
print(response.json())

# Using DeepSeek Cloud API
response = requests.post(
    "http://localhost:5000/generate",
    json={"age": 15, "provider": "deepseek"}
)
print(response.json())
```

---

### 3. Get Test Status

Get the current status of a test generation.

**Endpoint:** `GET /status/<test_id>`

**Path Parameters:**
- `test_id` (string, required): The test ID returned from the generate endpoint

**Response (Generating):**
```json
{
  "success": true,
  "test_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "generating",
  "progress": "Completed branch 2/4: Using Emotions to Facilitate Thought",
  "current_section": "branch_2",
  "provider": "ollama",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": null,
  "file_path": null
}
```

**Response (Completed):**
```json
{
  "success": true,
  "test_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": "completed",
  "current_section": "completed",
  "provider": "ollama",
  "created_at": "2024-01-01T12:00:00",
  "completed_at": "2024-01-01T12:05:00",
  "file_path": "tests/15/01_01_2024_550e8400.txt"
}
```

**Response (Error):**
```json
{
  "success": false,
  "error": "Test not found"
}
```

**Status Values:**
- `"generating"` - Test is currently being generated
- `"completed"` - Test generation is complete

**Example using cURL:**
```bash
curl "http://localhost:5000/status/550e8400-e29b-41d4-a716-446655440000"
```

**Example using Python:**
```python
import requests

test_id = "550e8400-e29b-41d4-a716-446655440000"
response = requests.get(f"http://localhost:5000/status/{test_id}")
print(response.json())
```

---

### 4. List All Tests

Get a list of all generated tests.

**Endpoint:** `GET /tests`

**Response:**
```json
{
  "success": true,
  "tests": [
    {
      "test_id": "550e8400-e29b-41d4-a716-446655440000",
      "age": 15,
      "status": "completed",
      "progress": "completed",
      "current_section": "completed",
      "provider": "ollama",
      "created_at": "2024-01-01T12:00:00",
      "completed_at": "2024-01-01T12:05:00",
      "file_path": "tests/15/01_01_2024_550e8400.txt"
    },
    {
      "test_id": "660e8400-e29b-41d4-a716-446655440001",
      "age": 16,
      "status": "generating",
      "progress": "Completed branch 1/4: Perceiving Emotions",
      "current_section": "branch_1",
      "provider": "deepseek",
      "created_at": "2024-01-01T12:10:00",
      "completed_at": null,
      "file_path": null
    }
  ]
}
```

**Example using cURL:**
```bash
curl "http://localhost:5000/tests"
```

---

## Configuration

You can configure the application using environment variables. Create a `.env` file in the project root (see `.env.example` for reference):

### Ollama Configuration (for local Ollama)
- `OLLAMA_BASE_URL`: Ollama API base URL (default: `http://localhost:11434`)
- `DEEPSEEK_MODEL`: Ollama model name (default: `deepseek:7b`)

### DeepSeek Cloud API Configuration
- `DEEPSEEK_API_URL`: DeepSeek Cloud API URL (default: `https://api.deepseek.com/v1/chat/completions`)
- `DEEPSEEK_API_KEY`: Your DeepSeek Cloud API key (required if using DeepSeek provider)
- `DEEPSEEK_CLOUD_MODEL`: DeepSeek Cloud model name (default: `deepseek-chat`)

### General Configuration
- `PROVIDER`: Default provider - `ollama` or `deepseek` (default: `ollama`)
- `SECRET_KEY`: Flask secret key
- `DEBUG`: Enable debug mode (default: `False`)
- `HOST`: Host to bind to (default: `0.0.0.0`)
- `PORT`: Port to bind to (default: `5000`)
- `TEMPERATURE`: Model temperature (default: `0.7`)
- `TOP_P`: Model top_p parameter (default: `0.9`)

### Environment Variables Table

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OLLAMA_BASE_URL` | Ollama API base URL | `http://localhost:11434` | No |
| `DEEPSEEK_MODEL` | Ollama model name | `deepseek:7b` | No |
| `DEEPSEEK_API_URL` | DeepSeek Cloud API URL | `https://api.deepseek.com/v1/chat/completions` | No |
| `DEEPSEEK_API_KEY` | DeepSeek Cloud API key | - | Yes (if using DeepSeek) |
| `DEEPSEEK_CLOUD_MODEL` | DeepSeek Cloud model name | `deepseek-chat` | No |
| `PROVIDER` | Default provider (`ollama` or `deepseek`) | `ollama` | No |
| `SECRET_KEY` | Flask secret key | `your-secret-key-here` | No |
| `DEBUG` | Enable debug mode | `False` | No |
| `HOST` | Host to bind to | `0.0.0.0` | No |
| `PORT` | Port to bind to | `5000` | No |
| `TEMPERATURE` | Model temperature | `0.7` | No |
| `TOP_P` | Model top_p parameter | `0.9` | No |

### Setting up DeepSeek Cloud API

1. Get your API key from [DeepSeek Platform](https://platform.deepseek.com/)
2. Add it to your `.env` file:
```
DEEPSEEK_API_KEY=your-api-key-here
PROVIDER=deepseek
```

### Setting up Ollama

1. Install and run Ollama:
```bash
ollama serve
```

2. Pull the DeepSeek model:
```bash
ollama pull deepseek:7b
```

3. Set environment variables (optional, defaults shown):
```bash
export OLLAMA_BASE_URL=http://localhost:11434
export DEEPSEEK_MODEL=deepseek:7b
export PROVIDER=ollama
```

---

## Test Structure

Each generated test contains 12 questions organized into 4 branches:

1. **Branch 1: Perceiving Emotions** (3 questions)
   - Identifying emotions in facial expressions, body language, tone, and situations

2. **Branch 2: Using Emotions to Facilitate Thought** (3 questions)
   - Understanding which emotions are helpful for specific tasks

3. **Branch 3: Understanding Emotions** (3 questions)
   - Comprehending how emotions arise, evolve, and combine

4. **Branch 4: Managing Emotions** (3 questions)
   - Regulating emotions effectively

Each question includes:
- Scenario/Stimulus (age-appropriate)
- Multiple choice options (4-5 options)
- Expert consensus scores (1-5 points per answer)
- Correct answer explanation

---

## File Storage

Tests are saved to the `tests/` directory, organized by age:
```
tests/
  ├── 12/
  │   └── 01_01_2024_550e8400.txt
  ├── 15/
  │   └── 01_01_2024_660e8400.txt
  └── 18/
      └── 01_01_2024_770e8400.txt
```

Old tests are automatically cleaned up after 24 hours.

---

## Error Handling

All endpoints return standardized error responses:

```json
{
  "success": false,
  "error": "Error message here"
}
```

**Common HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid parameters)
- `404` - Not Found (test not found)
- `500` - Internal Server Error

---

## Example Workflow

1. **Generate a test:**
```bash
curl -X POST "http://localhost:5000/generate" \
     -H "Content-Type: application/json" \
     -d '{"age": 15, "provider": "ollama"}'
```

Response:
```json
{
  "success": true,
  "test_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "generating",
  "provider": "ollama",
  "message": "Test generation started"
}
```

2. **Check status:**
```bash
curl "http://localhost:5000/status/550e8400-e29b-41d4-a716-446655440000"
```

3. **Wait for completion and check again:**
```bash
curl "http://localhost:5000/status/550e8400-e29b-41d4-a716-446655440000"
```

Response:
```json
{
  "success": true,
  "test_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": "completed",
  "file_path": "tests/15/01_01_2024_550e8400.txt"
}
```

4. **Read the generated test file:**
```bash
cat tests/15/01_01_2024_550e8400.txt
```

---

## Notes

- Test generation is asynchronous. Use the status endpoint to check progress.
- Tests are generated section-by-section (4 branches) to avoid token limits.
- Generated tests are automatically cleaned up after 24 hours.
- The API supports CORS for cross-origin requests.
- The API uses a thread pool with a maximum of 3 concurrent workers for test generation.
- No rate limiting is currently implemented.
