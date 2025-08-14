import os
import logging
import httpx
from flask import Flask, request, jsonify, render_template
from openai import OpenAI

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)

# Initialize OpenAI client with proxy support
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
HTTP_PROXY = os.environ.get("HTTP_PROXY")
HTTPS_PROXY = os.environ.get("HTTPS_PROXY")

if not OPENAI_API_KEY:
    logging.warning("OPENAI_API_KEY not found in environment variables")

# Create HTTP client with proxy if provided
http_client = None
if HTTP_PROXY or HTTPS_PROXY:
    proxies = {}
    if HTTP_PROXY:
        proxies["http://"] = HTTP_PROXY
        logging.info(f"Using HTTP proxy: {HTTP_PROXY}")
    if HTTPS_PROXY:
        proxies["https://"] = HTTPS_PROXY
        logging.info(f"Using HTTPS proxy: {HTTPS_PROXY}")
    
    http_client = httpx.Client(proxy=HTTPS_PROXY or HTTP_PROXY)

openai_client = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=http_client
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

        # Generate image using OpenAI DALL-E
        # the newest OpenAI model is "dall-e-3" which was released after knowledge cutoff
        # do not change this unless explicitly requested by the user
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size=size,
            quality="standard"
        )

        if response and response.data and len(response.data) > 0:
            image_url = response.data[0].url
        else:
            raise Exception("No image data returned from OpenAI API")
        
        logging.info("Image generated successfully")

        return jsonify({
            "success": True,
            "image_url": image_url,
            "prompt": prompt,
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

@app.route('/health')
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "DALL-E Image Generation API",
        "openai_configured": openai_client is not None
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
