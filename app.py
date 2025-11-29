from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import re
from datetime import datetime, timedelta
import uuid
from typing import Dict, List, Any, Optional, Tuple
import os
import threading
from concurrent.futures import ThreadPoolExecutor
from section_prompts import get_section_prompts
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Simple configuration
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
DEEPSEEK_MODEL = os.getenv('DEEPSEEK_MODEL', 'deepseek:7b')
DEEPSEEK_API_URL = os.getenv('DEEPSEEK_API_URL', 'https://api.deepseek.com/v1/chat/completions')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
DEEPSEEK_CLOUD_MODEL = os.getenv('DEEPSEEK_CLOUD_MODEL', 'deepseek-chat')
PROVIDER = os.getenv('PROVIDER', 'ollama').lower()  # 'ollama' or 'deepseek'
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', 5000))
TEMPERATURE = float(os.getenv('TEMPERATURE', 0.7))
TOP_P = float(os.getenv('TOP_P', 0.9))

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = SECRET_KEY

# Simple in-memory storage for tests with thread safety
tests_storage = {}
storage_lock = threading.RLock()

# Thread pool for asynchronous test generation
executor = ThreadPoolExecutor(max_workers=3)

# Configuration for cleanup
MAX_TEST_AGE_HOURS = 24  # Remove tests older than 24 hours
MAX_STORED_TESTS = 100   # Maximum number of tests to keep in memory


class EQTestGenerator:
    def __init__(self, provider: str = None, ollama_url: str = None, model: str = None):
        self.provider = provider or PROVIDER
        self.ollama_url = ollama_url or OLLAMA_BASE_URL
        self.model = model or DEEPSEEK_MODEL
        self.session = requests.Session()
    
    def _generate_test_section_by_section(self, age: int, test_id: str, provider: str = None) -> Dict[str, Any]:
        """Generate a complete EQ test section by section to avoid token limits"""
        # Use provided provider or default
        current_provider = provider or self.provider
        
        # Validate age parameter
        if not (12 <= age <= 18):
            return {
                "success": False,
                "error": "Age must be between 12 and 18"
            }
        
        # Get section prompts
        section_prompts = get_section_prompts(age)
        
        # Define section order (4 branches)
        section_order = [
            "branch_1", "branch_2", "branch_3", "branch_4"
        ]
        
        # Initialize test content
        test_content = ""
        
        # Generate each section
        for i, section_name in enumerate(section_order):
            # Get section prompt
            section_prompt = section_prompts[section_name]
            
            # Generate section content using the selected provider
            try:
                if current_provider == 'deepseek':
                    section_content = self._call_deepseek_cloud(section_prompt)
                else:  # default to ollama
                    section_content = self._call_ollama(section_prompt)
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Failed to generate section {section_name}: {str(e)}"
                }
            
            if not section_content:
                return {
                    "success": False,
                    "error": f"Failed to generate section: {section_name}"
                }
            
            # Clean up any redacted reasoning if present
            cleaned = re.sub(r'<think>.*?</think>', '', section_content, flags=re.DOTALL)
            cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL)
            
            # Append to test content
            test_content += cleaned + "\n\n"
            
            # Update progress in test record with thread safety
            with storage_lock:
                if test_id in tests_storage:
                    branch_names = {
                        "branch_1": "Perceiving Emotions",
                        "branch_2": "Using Emotions to Facilitate Thought",
                        "branch_3": "Understanding Emotions",
                        "branch_4": "Managing Emotions"
                    }
                    branch_name = branch_names.get(section_name, section_name)
                    tests_storage[test_id].update({
                        "status": "generating",
                        "progress": f"Completed branch {i+1}/{len(section_order)}: {branch_name}",
                        "current_section": section_name,
                        "provider": current_provider
                    })
        
        # Validate complete test structure before saving
        is_valid, validation_details = self._validate_test_schema(test_content)
        if not is_valid:
            error_message = "Schema validation failed"
            if validation_details:
                error_message += f": {'; '.join(validation_details)}"
            with storage_lock:
                if test_id in tests_storage:
                    tests_storage[test_id].update({
                        "status": "failed",
                        "progress": "validation_failed",
                        "current_section": "validation",
                        "error": error_message,
                        "provider": current_provider
                    })
            return {
                "success": False,
                "test_id": test_id,
                "error": error_message,
                "provider": current_provider
            }

        # Save complete test to file
        filepath = self._save_test_to_file(test_content, age, test_id)
        
        # Update test record with completion and cleanup old tests
        with storage_lock:
            tests_storage[test_id].update({
                "status": "completed",
                "progress": "completed",
                "current_section": "completed",
                "file_path": filepath,
                "completed_at": datetime.now().isoformat(),
                "provider": current_provider
            })
            
            # Cleanup old tests
            self._cleanup_old_tests()
        
        return {
            "success": True,
            "test_id": test_id,
            "message": "Test generated successfully",
            "file_path": filepath,
            "provider": current_provider
        }
    
    def _call_ollama(self, prompt: str) -> str:
        """Call Ollama API with the given prompt"""
        url = f"{self.ollama_url}/api/generate"
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": TEMPERATURE,
                "top_p": TOP_P,
            }
        }
        
        response = self.session.post(url, json=payload, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        if 'response' in result:
            return result['response']
        else:
            raise Exception("Invalid response format from Ollama API")
    
    def _call_deepseek_cloud(self, prompt: str) -> str:
        """Call DeepSeek Cloud API with the given prompt"""
        if not DEEPSEEK_API_KEY:
            raise Exception("DEEPSEEK_API_KEY not configured. Please set it in your environment variables.")
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": DEEPSEEK_CLOUD_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": TEMPERATURE,
            "top_p": TOP_P
        }
        
        response = self.session.post(DEEPSEEK_API_URL, headers=headers, json=data, timeout=300)
        response.raise_for_status()
        
        result = response.json()
        
        if 'choices' in result and len(result['choices']) > 0:
            return result['choices'][0]['message']['content']
        else:
            raise Exception("Invalid response format from DeepSeek Cloud API")

    def _validate_test_schema(self, content: str) -> Tuple[bool, List[str]]:
        """Validate that generated test content follows the expected schema."""
        errors: List[str] = []

        if not content or not content.strip():
            return False, ["Test content is empty"]

        expected_branches = [
            "Branch 1: Perceiving Emotions",
            "Branch 2: Using Emotions to Facilitate Thought",
            "Branch 3: Understanding Emotions",
            "Branch 4: Managing Emotions"
        ]

        branch_regex = re.compile(r"(Branch\s+\d:\s+[^\n]+)")
        sections = branch_regex.split(content)

        # sections structure: [prefix?, header1, body1, header2, body2, ...]
        if len(sections) < 2:
            return False, ["No branches found in generated content"]

        # Detect unexpected text before the first branch
        preface = sections[0].strip()
        if preface:
            errors.append("Unexpected text found before the first branch")

        branches_found = []
        for idx in range(1, len(sections), 2):
            header = sections[idx].strip()
            body = sections[idx + 1] if idx + 1 < len(sections) else ""
            branches_found.append((header, body))

        if len(branches_found) != len(expected_branches):
            errors.append(
                f"Expected {len(expected_branches)} branches but found {len(branches_found)}"
            )

        for expected_branch, branch_data in zip(expected_branches, branches_found):
            found_header, body = branch_data

            if found_header != expected_branch:
                errors.append(f"Expected branch header '{expected_branch}' but found '{found_header}'")

            question_pattern = re.compile(
                r"Question\s+(\d+)\s*(.*?)(?=(?:\nQuestion\s+\d+)|\Z)",
                re.DOTALL | re.IGNORECASE
            )
            question_blocks = question_pattern.findall(body)

            if len(question_blocks) != 3:
                errors.append(
                    f"{expected_branch}: Expected 3 questions but found {len(question_blocks)}"
                )
                continue

            for question_number_str, question_block in question_blocks:
                question_number = question_number_str.strip()
                block = question_block.strip()

                if "Scenario & Question:" not in block:
                    errors.append(
                        f"{expected_branch} Question {question_number}: Missing 'Scenario & Question' section"
                    )

                if "Options:" not in block:
                    errors.append(
                        f"{expected_branch} Question {question_number}: Missing 'Options' section"
                    )
                    continue

                options = re.findall(r"^[A-E]\)\s+.+", block, flags=re.MULTILINE)
                if len(options) < 4:
                    errors.append(
                        f"{expected_branch} Question {question_number}: Expected at least 4 options but found {len(options)}"
                    )

                if "Expert Consensus Scores:" not in block:
                    errors.append(
                        f"{expected_branch} Question {question_number}: Missing 'Expert Consensus Scores' section"
                    )
                else:
                    scores_section_match = re.search(
                        r"Expert\s+Consensus\s+Scores:(.*?)(?:\n{2,}|\Z)",
                        block,
                        flags=re.DOTALL | re.IGNORECASE
                    )
                    scores_section = scores_section_match.group(1) if scores_section_match else ""
                    missing_scores = []
                    for option_line in options:
                        option_letter = option_line.split(")", 1)[0].strip()
                        if option_letter and option_letter not in scores_section:
                            missing_scores.append(option_letter)
                    if missing_scores:
                        errors.append(
                            f"{expected_branch} Question {question_number}: Missing scores for options {', '.join(sorted(set(missing_scores)))}"
                        )

        return (len(errors) == 0, errors)
    
    def _save_test_to_file(self, content: str, age: int, test_id: str) -> str:
        """Save test content to file with security validation"""
        # Validate test_id to prevent path traversal
        if not re.match(r'^[a-zA-Z0-9\-_]+', test_id):
            raise ValueError("Invalid test_id format")
        
        # Validate age parameter
        if not isinstance(age, int) or not (12 <= age <= 18):
            raise ValueError("Invalid age parameter")
        
        # Create age-specific directory
        age_dir = os.path.join('tests', str(age))
        os.makedirs(age_dir, exist_ok=True)
        
        # Generate filename with current date and test_id for uniqueness
        current_date = datetime.now().strftime('%d_%m_%Y')
        filename = f"{current_date}_{test_id[:8]}.txt"
        filepath = os.path.join(age_dir, filename)
        
        # Write content to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    
    def _cleanup_old_tests(self):
        """Remove old test records from memory"""
        current_time = datetime.now()
        cutoff_time = current_time - timedelta(hours=MAX_TEST_AGE_HOURS)
        
        # Remove old test records
        old_test_ids = []
        for test_id, test_record in tests_storage.items():
            created_at = datetime.fromisoformat(test_record['created_at'])
            if created_at < cutoff_time:
                old_test_ids.append(test_id)
        
        for test_id in old_test_ids:
            # Also remove the associated file if it exists
            test_record = tests_storage.get(test_id)
            if test_record and 'file_path' in test_record:
                try:
                    if os.path.exists(test_record['file_path']):
                        os.remove(test_record['file_path'])
                except OSError:
                    pass  # Ignore file removal errors
            del tests_storage[test_id]
        
        # If we still have too many tests, remove the oldest ones
        if len(tests_storage) > MAX_STORED_TESTS:
            sorted_tests = sorted(
                tests_storage.items(), 
                key=lambda x: datetime.fromisoformat(x[1]['created_at'])
            )
            excess_count = len(tests_storage) - MAX_STORED_TESTS
            for i in range(excess_count):
                test_id = sorted_tests[i][0]
                test_record = tests_storage.get(test_id)
                if test_record and 'file_path' in test_record:
                    try:
                        if os.path.exists(test_record['file_path']):
                            os.remove(test_record['file_path'])
                    except OSError:
                        pass
                del tests_storage[test_id]


# Initialize generator
test_generator = EQTestGenerator()


def create_error_response(message: str, status_code: int = 400) -> tuple:
    """Create standardized error response"""
    return jsonify({
        "success": False,
        "error": message
    }), status_code


def create_success_response(data: dict = None, message: str = None) -> dict:
    """Create standardized success response"""
    response = {"success": True}
    if data:
        response.update(data)
    if message:
        response["message"] = message
    return response


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })


@app.route('/generate', methods=['POST'])
@app.route('/create-eq-test', methods=['POST'])
def generate_test():
    """Generate a new EQ test"""
    try:
        data = request.get_json()
        age = data.get('age', 15)
        provider = data.get('provider', PROVIDER).lower()  # Optional: 'ollama' or 'deepseek'
        
        # Validate age
        if not (12 <= age <= 18):
            return create_error_response("Age must be between 12 and 18", 400)
        
        # Validate provider
        if provider not in ['ollama', 'deepseek']:
            return create_error_response("Provider must be either 'ollama' or 'deepseek'", 400)
        
        # Check if DeepSeek API key is required
        if provider == 'deepseek' and not DEEPSEEK_API_KEY:
            return create_error_response("DEEPSEEK_API_KEY not configured. Please set it in your environment variables.", 400)
        
        # Generate unique test ID
        test_id = str(uuid.uuid4())
        
        # Create test record with thread safety
        with storage_lock:
            tests_storage[test_id] = {
                "test_id": test_id,
                "age": age,
                "status": "generating",
                "progress": "0/4",
                "current_section": "initializing",
                "provider": provider,
                "created_at": datetime.now().isoformat()
            }
        
        # Submit generation task to thread pool
        future = executor.submit(
            test_generator._generate_test_section_by_section,
            age, test_id, provider
        )
        
        return jsonify(create_success_response({
            "test_id": test_id,
            "status": "generating",
            "provider": provider
        }, "Test generation started"))
        
    except Exception as e:
        return create_error_response(str(e), 500)


@app.route('/status/<test_id>', methods=['GET'])
def get_test_status(test_id: str):
    """Get the status of a test generation"""
    with storage_lock:
        if test_id not in tests_storage:
            return jsonify({
                "success": False,
                "error": "Test not found"
            }), 404
        
        test_record = tests_storage[test_id].copy()
    return jsonify({
        "success": True,
        "test_id": test_id,
        "status": test_record["status"],
        "progress": test_record.get("progress", "unknown"),
        "current_section": test_record.get("current_section", "unknown"),
        "provider": test_record.get("provider", "unknown"),
        "created_at": test_record["created_at"],
        "completed_at": test_record.get("completed_at"),
        "file_path": test_record.get("file_path")
    })


@app.route('/tests', methods=['GET'])
def list_tests():
    """List all generated tests"""
    with storage_lock:
        return jsonify({
            "success": True,
            "tests": list(tests_storage.values())
        })


if __name__ == '__main__':
    app.run(host=HOST, port=PORT, debug=DEBUG)
