from flask import Flask, request, jsonify,render_template
from flask_cors import CORS
import requests
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

@app.route('/')
def home():
    return render_template('index.html')
        
# Stability AI API configuration
STABILITY_API_KEY = os.getenv("STABILITY_API_KEY")
STABILITY_API_URL = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        # Get prompt from request
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        if not STABILITY_API_KEY:
            return jsonify({'error': 'API key not configured'}), 500
        
        # Prepare request to Stability AI
        headers = {
            "Authorization": f"Bearer {STABILITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {
            "text_prompts": [
                {
                    "text": prompt,
                    "weight": 1
                }
            ],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }
        
        # Make request to Stability AI
        response = requests.post(
            STABILITY_API_URL,
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            error_message = response.json().get('message', 'Unknown error')
            return jsonify({'error': f'Stability AI error: {error_message}'}), response.status_code
        
        # Extract image from response
        response_data = response.json()
        
        if 'artifacts' in response_data and len(response_data['artifacts']) > 0:
            image_data = response_data['artifacts'][0]['base64']
            
            # Return base64 image
            return jsonify({
                'image': f"data:image/png;base64,{image_data}",
                'success': True
            })
        else:
            return jsonify({'error': 'No image generated'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'message': 'Server is running'})

if __name__ == '__main__':
    if not STABILITY_API_KEY:
        print("WARNING: STABILITY_API_KEY not found in environment variables")
        print("Please create a .env file with your API key:")
        print("STABILITY_API_KEY=your_api_key_here")
    
    print("Starting server on http://localhost:5000")
    app.run(debug=True, port=5000)     
