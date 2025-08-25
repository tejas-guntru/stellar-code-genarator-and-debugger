import os
import json
import uuid
import shutil
import logging
import subprocess
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from google.cloud import storage
import google.generativeai as genai

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Google Gemini
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    logger.error("GOOGLE_API_KEY environment variable not set!")
    raise ValueError("GOOGLE_API_KEY environment variable is required")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Constants
MAX_RETRIES = 3
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Docker configuration
DOCKER_IMAGES = {
    "python": {
        "image": "stellar-python-sandbox:3.12", 
        "file": "main.py", 
        "command": ["python", "main.py"]
    },
    "cpp": {
        "image": "stellar-cpp-sandbox:latest", 
        "file": "main.cpp", 
        "command": ["g++", "main.cpp", "-o", "main", "&&", "./main"]
    },
    "java": {
        "image": "stellar-java-sandbox:latest", 
        "file": "Main.java", 
        "command": ["javac", "Main.java", "&&", "java", "Main"]
    },
    "html": {
        "image": None, 
        "file": "index.html", 
        "command": None
    }
}

def stream_message(event, data):
    """Helper function to format server-sent events"""
    logger.debug(f"Streaming: {event} - {data}")
    message = json.dumps(data)
    yield f"event: {event}\n"
    yield f"data: {message}\n\n"

def generation_logic(prompt, language, uploaded_file_info=None):
    """Core logic for code generation"""
    logger.debug(f"Generation started: prompt={prompt}, language={language}, file_info={uploaded_file_info}")
    
    try:
        for attempt in range(MAX_RETRIES):
            yield from stream_message("status", {
                "message": f"Attempt {attempt + 1}/{MAX_RETRIES}: Generating code..."
            })
            
            try:
                # Prepare the prompt with file context if provided
                full_prompt = prompt
                if uploaded_file_info:
                    full_prompt = f"File content:\n{uploaded_file_info['content']}\n\nPrompt: {prompt}"
                
                logger.debug(f"Sending prompt to Gemini: {full_prompt[:100]}...")
                
                # Generate code using Gemini
                response = model.generate_content(full_prompt)
                
                if not response:
                    logger.warning(f"Attempt {attempt + 1}: No response from Gemini")
                    continue
                
                generated_code = response.text
                logger.debug(f"Generated code (first 100 chars): {generated_code[:100]}...")
                
                # Send the generated code
                yield from stream_message("final_code", {
                    "code": generated_code,
                    "output": ""  # You can add code execution output here if needed
                })
                return
                
            except Exception as e:
                logger.error(f"Attempt {attempt + 1} failed: {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise
                yield from stream_message("status", {
                    "message": f"Attempt failed: {str(e)}. Retrying..."
                })
    
    except Exception as e:
        logger.error(f"Generation failed after {MAX_RETRIES} attempts: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        yield from stream_message("error", {
            "message": f"Code generation failed: {str(e)}"
        })

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    """Endpoint for code generation"""
    try:
        logger.debug(f"Received {request.method} request to /generate")
        
        if request.method == 'POST':
            data = request.get_json()
            if not data:
                logger.warning("No JSON data provided in POST request")
                return Response(
                    'event: error\ndata: {"message": "No JSON data provided"}\n\n',
                    content_type='text/event-stream'
                )
            prompt = data.get('prompt')
            language = data.get('language')
            uploaded_file_info = data.get('uploaded_file_info')
        else:  # GET request
            prompt = request.args.get('prompt')
            language = request.args.get('language')
            uploaded_file_info = None
        
        logger.debug(f"Request parameters: prompt={prompt}, language={language}")
        
        if not prompt:
            logger.warning("Missing required parameter: prompt")
            return Response(
                'event: error\ndata: {"message": "Prompt is required"}\n\n',
                content_type='text/event-stream'
            )
        
        if not language:
            logger.warning("Missing required parameter: language")
            return Response(
                'event: error\ndata: {"message": "Language is required"}\n\n',
                content_type='text/event-stream'
            )
        
        return Response(
            generation_logic(prompt, language, uploaded_file_info), 
            content_type='text/event-stream'
        )
    
    except Exception as e:
        logger.error("Error in generate endpoint:", exc_info=True)
        return Response(
            f'event: error\ndata: {{"message": "Server error: {str(e)}"}}\n\n',
            content_type='text/event-stream'
        )

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Simple test endpoint to verify the server is working"""
    try:
        logger.debug("Test endpoint called")
        # Test Gemini API connection
        test_response = model.generate_content("Say 'Hello, World!'")
        return jsonify({
            "status": "success",
            "message": "Server is working",
            "gemini_response": test_response.text
        })
    except Exception as e:
        logger.error("Test endpoint failed:", exc_info=True)
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Check if Docker and all services are working"""
    status = {
        "flask": "running",
        "docker": "unknown",
        "sandboxes": {}
    }
    
    # Check Docker
    try:
        docker_info = subprocess.run(["docker", "info"], capture_output=True, text=True)
        status["docker"] = "running" if docker_info.returncode == 0 else "not running"
    except FileNotFoundError:
        status["docker"] = "not installed"
    
    # Check each sandbox container
    for language in DOCKER_IMAGES:
        if language == "html":
            continue  # HTML doesn't need a sandbox
            
        container_name = f"{language}-sandbox"
        try:
            check = subprocess.run(
                ["docker", "inspect", "--format={{.State.Running}}", container_name],
                capture_output=True, text=True
            )
            status["sandboxes"][language] = "running" if check.returncode == 0 and "true" in check.stdout else "not running"
        except Exception:
            status["sandboxes"][language] = "error checking"
    
    return jsonify(status)

def run_code_locally(code, language, uploaded_file_info=None):
    """Fallback function if Docker is not available"""
    if language == "python":
        try:
            # WARNING: This is a security risk for production use!
            # Only use for development with trusted code
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                f.flush()
                
                result = subprocess.run(
                    ["python", f.name],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                os.unlink(f.name)
                return result.returncode, result.stdout, result.stderr
                
        except Exception as e:
            return 1, "", f"Local execution error: {str(e)}"
    
    else:
        return 1, "", f"Local execution not supported for {language}"

def run_code_in_docker(code, language, uploaded_file_info=None):
    lang_config = DOCKER_IMAGES.get(language)
    if not lang_config or not lang_config.get("image"):
        return 0, "Language not supported for server-side execution.", ""
    
    # Check if Docker is running
    try:
        subprocess.run(["docker", "info"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        logger.warning("Docker not available, falling back to local execution")
        return run_code_locally(code, language, uploaded_file_info)
    
    temp_dir = f"./temp_run_{uuid.uuid4()}"
    os.makedirs(temp_dir, exist_ok=True)
    
    try:
        code_file_path = os.path.join(temp_dir, lang_config["file"])
        with open(code_file_path, "w", encoding='utf-8') as f:
            f.write(code)
        
        if uploaded_file_info:
            source_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file_info['id'])
            dest_path = os.path.join(temp_dir, uploaded_file_info['name'])
            if os.path.exists(source_path):
                shutil.copy(source_path, dest_path)
        
        # Use the container name if using Docker Compose
        container_name = f"{language}-sandbox"
        
        # Try to use the specific container, or fall back to creating a new one
        try:
            # Check if our sandbox container exists and is running
            check_container = subprocess.run(
                ["docker", "inspect", "--format={{.State.Running}}", container_name],
                capture_output=True, text=True
            )
            
            if check_container.returncode != 0 or "true" not in check_container.stdout:
                # Container doesn't exist or isn't running, create a new one
                docker_command = ["docker", "run", "--rm", "-v", f"{os.path.abspath(temp_dir)}:/app", "-w", "/app", lang_config["image"]]
            else:
                # Use the existing container
                docker_command = ["docker", "exec", "-i", "-w", "/app", container_name]
                
        except Exception:
            # Fallback to creating a new container
            docker_command = ["docker", "run", "--rm", "-v", f"{os.path.abspath(temp_dir)}:/app", "-w", "/app", lang_config["image"]]
        
        docker_command.extend(lang_config["command"])
        
        process = subprocess.Popen(
            docker_command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            text=True, 
            encoding='utf-8'
        )
        stdout, stderr = process.communicate(timeout=30)
        return_code = process.returncode
        
        return return_code, stdout, stderr
        
    except subprocess.TimeoutExpired:
        process.kill()
        stdout, stderr = "", "Execution timed out after 30 seconds."
        return_code = 1
        return return_code, stdout, stderr
        
    except Exception as e:
        return 1, "", f"Docker execution error: {str(e)}"
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint for file uploads"""
    try:
        logger.debug("File upload endpoint called")
        if 'file' not in request.files:
            logger.warning("No file provided in upload request")
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            logger.warning("Empty filename in upload request")
            return jsonify({"error": "No file selected"}), 400
        
        # Read and process the file
        content = file.read().decode('utf-8')
        logger.debug(f"File uploaded: {file.filename} (size: {len(content)} bytes)")
        
        return jsonify({
            "file_id": "temp_id",  # You can generate a unique ID if needed
            "filename": file.filename,
            "preview": content[:100] + "...",  # Preview first 100 chars
            "content": content
        })
        
    except Exception as e:
        logger.error("File upload failed:", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Check if running in debug mode
    debug_mode = os.getenv('FLASK_ENV') == 'development'
    
    # Log startup information
    logger.info(f"Starting Flask server in {'debug' if debug_mode else 'production'} mode")
    logger.info(f"CORS enabled, allowing all origins")
    logger.info(f"Gemini API configured with model: gemini-pro")
    
    # Start the server
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)
