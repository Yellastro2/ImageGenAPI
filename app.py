import os
import logging
import httpx
from flask import Flask, request, jsonify, render_template
from openai import OpenAI
from flask_cors import CORS
import base64
import uuid
import mimetypes

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Глушим httpx дебаг (который дергает OpenAI SDK)
logging.getLogger("httpx").setLevel(logging.ERROR)
logging.getLogger("httpcore").setLevel(logging.ERROR)
logging.getLogger("openai").setLevel(logging.ERROR)
# Отключаем полностью
logging.getLogger("openai").disabled = True

# Create Flask app
app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": [
            r"https://*.tilda.ru",
            r"https://*.tilda.сс",
            r"https://*.tistools.ru",
            r"https://*.vseinstrumenti.ru"
        ]
    }
})
app.config['GENERATED_FOLDER'] = os.path.join(app.root_path, 'static', 'generated')
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Initialize OpenAI client with selective proxy support
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
OPENAI_PROXY = os.environ.get("OPENAI_PROXY")  # Специальная переменная только для OpenAI

if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY not found in environment variables")

# Create HTTP client with proxy only for OpenAI if specified
openai_http_client = None
if OPENAI_PROXY:
    logging.info(f"Using proxy for OpenAI requests: {OPENAI_PROXY}")
    openai_http_client = httpx.Client(proxy=OPENAI_PROXY)
else:
    logging.info("No proxy specified for OpenAI - using direct connection")

openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=openai_http_client
) if OPENAI_API_KEY else None

@app.route('/')
def index():
    """Serve the API documentation page"""
    return render_template('index.html')

@app.route('/api/generate-image', methods=['POST'])
def generate_image():
    """
    Generate an image using OpenAI DALL-E API
    
    Expected JSON payload:
    {
        "prompt": "A detailed description of the image to generate",
        "size": "1024x1024" (optional, defaults to 1024x1024)
    }
    
    Returns:
    {
        "success": true,
        "image_url": "https://...",
        "prompt": "The original prompt"
    }
    """
    try:
        # Check if OpenAI client is available
        if not openai_client:
            return jsonify({
                "success": False,
                "error": "OpenAI API key not configured",
                "message": "Please set OPENAI_API_KEY environment variable"
            }), 500

        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON",
                "message": "Request must contain valid JSON data"
            }), 400

        # Validate prompt
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({
                "success": False,
                "error": "Missing prompt",
                "message": "Please provide a 'prompt' field with your image description"
            }), 400

        if len(prompt) > 1000:
            return jsonify({
                "success": False,
                "error": "Prompt too long",
                "message": "Prompt must be 1000 characters or less"
            }), 400

        # Get optional size parameter
        size = data.get('size', '1024x1024')
        valid_sizes = ['256x256', '512x512', '1024x1024', '1792x1024', '1024x1792']
        if size not in valid_sizes:
            return jsonify({
                "success": False,
                "error": "Invalid size",
                "message": f"Size must be one of: {', '.join(valid_sizes)}"
            }), 400

        logging.info(f"Generating image with prompt: {prompt[:100]}...")
        model = data.get("model", "gpt-image-1")

        params = {
            "model": model,
            "prompt": prompt,
            "size": size
        }

        if model == "gpt-image-1":
            params["quality"] = "medium"
        elif model == "dall-e-3":
            params["quality"] = "standard"
            params["n"] = 1
            params["response_format"] = "url"

        response = openai_client.images.generate(**params)

        if not response or not response.data:
            return jsonify({"success": False, "error": "No image data"}), 500

        if model == "gpt-image-1":
            # Сохраняем base64 в файл
            b64_data = response.data[0].b64_json
            img_bytes = base64.b64decode(b64_data)
            filename = f"{uuid.uuid4().hex}.png"
            file_path = os.path.join(app.config['GENERATED_FOLDER'], filename)
            with open(file_path, "wb") as f:
                f.write(img_bytes)
            image_url = f"{request.host_url}static/generated/{filename}"
            logging.info(f"Image saved to {file_path}")

        else:  # dall-e-3
            image_url = response.data[0].url
            filename = "dall-e-3.png"

        logging.info("Image generated successfully")
        logging.info(f"Image URL: {image_url}")

        return jsonify({
            "success": True,
            "image_url": image_url,
            "prompt": prompt,
            "filename": filename,
            "size": size
        })

    except Exception as e:
        logging.error(f"Error generating image: {str(e)}")
        
        # Handle specific OpenAI errors
        if "content_policy_violation" in str(e).lower():
            return jsonify({
                "success": False,
                "error": "Content policy violation",
                "message": "The prompt violates OpenAI's content policy. Please try a different description."
            }), 400
        elif "rate_limit" in str(e).lower():
            return jsonify({
                "success": False,
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later."
            }), 429
        elif "insufficient_quota" in str(e).lower():
            return jsonify({
                "success": False,
                "error": "Quota exceeded",
                "message": "OpenAI API quota has been exceeded."
            }), 429
        else:
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred while generating the image."
            }), 500

@app.route('/api/generate-text', methods=['POST'])
def generate_text():
    """
    Generate text using OpenAI GPT API with optional image input
    
    Expected JSON payload:
    {
        "prompt": "Your text prompt or question",
        "image_url": "https://example.com/image.jpg" (optional, for vision tasks),
        "max_tokens": 1000 (optional, defaults to 1000),
        "model": "gpt-4" (optional, defaults to gpt-4, auto-switches to gpt-4-vision-preview if image_url provided)
    }
    
    Returns:
    {
        "success": true,
        "text": "Generated text response",
        "prompt": "The original prompt",
        "model": "gpt-4",
        "has_image": false
    }
    """
    try:
        # Check if OpenAI client is available
        if not openai_client:
            return jsonify({
                "success": False,
                "error": "OpenAI API key not configured",
                "message": "Please set OPENAI_API_KEY environment variable"
            }), 500

        # Get JSON data from request
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error": "Invalid JSON",
                "message": "Request must contain valid JSON data"
            }), 400

        # Validate prompt
        prompt = data.get('prompt', '').strip()
        if not prompt:
            return jsonify({
                "success": False,
                "error": "Missing prompt",
                "message": "Please provide a 'prompt' field with your text query"
            }), 400

        if len(prompt) > 4000:
            return jsonify({
                "success": False,
                "error": "Prompt too long",
                "message": "Prompt must be 4000 characters or less"
            }), 400

        # Get optional parameters
        max_tokens = data.get('max_tokens', 1000)
        model = data.get('model', 'gpt-4o')
        image_url = data.get('image_url', '').strip()
        
        # Auto-switch to vision model if image is provided
        has_image = bool(image_url)
        if has_image and model in ['gpt-4', 'gpt-4-turbo']:
            model = 'gpt-4o'
        
        # Validate max_tokens
        if not isinstance(max_tokens, int) or max_tokens < 1 or max_tokens > 4000:
            return jsonify({
                "success": False,
                "error": "Invalid max_tokens",
                "message": "max_tokens must be an integer between 1 and 4000"
            }), 400

        # Validate model
        valid_models = ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo', 'gpt-4o']
        if model not in valid_models:
            return jsonify({
                "success": False,
                "error": "Invalid model",
                "message": f"Model must be one of: {', '.join(valid_models)}"
            }), 400

        logging.info(f"Generating text with model {model}, prompt: {prompt[:100]}... {'with image' if has_image else ''}")
        # Validate image URL if provided
        if image_url:
            if not (image_url.startswith('http://') or image_url.startswith('https://')):
                # Локальный файл — проверяем и готовим как файл
                
                local_path = image_url
                if not os.path.isabs(local_path):
                    local_path = os.path.join(app.config['GENERATED_FOLDER'], image_url)

                if not os.path.exists(local_path):
                    return jsonify({
                        "success": False,
                        "error": "File not found",
                        "message": f"Local image file not found: {local_path}"
                    }), 400

                mime_type, _ = mimetypes.guess_type(local_path)
                if mime_type is None:
                    mime_type = "image/png"
                logging.info(f"Local image file found: {local_path} with MIME type {mime_type}")

                with open(local_path, "rb") as f:
                    image_data = f.read()


                b64 = base64.b64encode(image_data).decode("utf-8")

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{b64}"
                                }
                            }
                        ]
                    }
                ]
            else:

                # Prepare messages based on whether image is provided
                if has_image:
                    messages = [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": image_url
                                    }
                                }
                            ]
                        }
                    ]
                else:
                    messages = [
                        {"role": "user", "content": prompt}
                    ]

        # Generate text using OpenAI GPT
        response = openai_client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )

        if response and response.choices and len(response.choices) > 0:
            generated_text = response.choices[0].message.content
        else:
            raise Exception("No text data returned from OpenAI API")
        
        logging.info("Text generated successfully")
        logging.info(f"Generated text: {generated_text[:100]}...")

        return jsonify({
            "success": True,
            "text": generated_text,
            "prompt": prompt,
            "model": model,
            "has_image": has_image,
            "image_url": image_url if has_image else None,
            "tokens_used": response.usage.total_tokens if response.usage else None
        })

    except Exception as e:
        logging.error(f"Error generating text: {str(e)}")
        
        # Handle specific OpenAI errors
        if "content_policy_violation" in str(e).lower():
            return jsonify({
                "success": False,
                "error": "Content policy violation",
                "message": "The prompt violates OpenAI's content policy. Please try a different query."
            }), 400
        elif "rate_limit" in str(e).lower():
            return jsonify({
                "success": False,
                "error": "Rate limit exceeded",
                "message": "Too many requests. Please try again later."
            }), 429
        elif "insufficient_quota" in str(e).lower():
            return jsonify({
                "success": False,
                "error": "Quota exceeded",
                "message": "OpenAI API quota has been exceeded."
            }), 429
        else:
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred while generating text."
            }), 500

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "DALL-E Image Generation API",
        "openai_configured": openai_client is not None,
        "proxy_configured": OPENAI_PROXY is not None,
        "proxy_url": OPENAI_PROXY if OPENAI_PROXY else "direct connection"
    })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": "Not found",
        "message": "The requested endpoint does not exist"
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        "success": False,
        "error": "Method not allowed",
        "message": "This endpoint does not support the requested HTTP method"
    }), 405

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
