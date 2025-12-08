import os
import io
import time
import json
from flask import Flask, render_template, request, send_file, jsonify
from datetime import datetime

# --- ChatterboxTTS Imports (Based on your story.py file) ---
# NOTE: Ensure these libraries (torchaudio, torch, chatterbox) are installed 
# in your Docker environment.
import torchaudio as ta
import torch
from chatterbox.tts import ChatterboxTTS

# --- Configuration ---
SAMPLES_FOLDER = 'static/samples'
LOG_FILE_PATH = 'visitor_logs.txt'

app = Flask(__name__, static_url_path='/static', template_folder='templates')

# Ensure required directories exist
if not os.path.exists(SAMPLES_FOLDER):
    os.makedirs(SAMPLES_FOLDER)

# --- TTS Model Initialization ---
# Automatically detect the best available device
if torch.cuda.is_available():
    device = "cuda"
elif torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

print(f"Using device: {device}")

# Initialize the model once globally
try:
    print("Loading ChatterboxTTS model...")
    # NOTE: This model load is the most resource-intensive step.
    tts_model = ChatterboxTTS.from_pretrained(device=device)
    # tts_model.eval()
    # tts_model.sr = 22050 # Ensure sample rate is set for torchaudio.save
    print("ChatterboxTTS model loaded successfully.")
except Exception as e:
    print(f"Error loading TTS model: {e}. Please check your Chatterbox installation.")
    tts_model = None

# --- Utility Functions ---

def get_real_client_ip(request):
    """
    Tries to get the client's IP from X-Forwarded-For header first, 
    then falls back to remote_addr (robust for Docker/Proxy setups).
    """
    if 'X-Forwarded-For' in request.headers:
        # X-Forwarded-For can contain multiple IPs. The first is usually the client.
        return request.headers['X-Forwarded-For'].split(',')[0].strip()
    return request.remote_addr

def list_sample_files():
    """Returns a list of .wav filenames in the samples directory."""
    full_path = os.path.join(app.root_path, SAMPLES_FOLDER)
    files = [f for f in os.listdir(full_path) if f.endswith('.wav')]
    return files

# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    """Renders the main page and passes available sample files to the template."""
    sample_files = list_sample_files()
    return render_template('index.html', sample_files=sample_files)


@app.route('/log_visit', methods=['POST'])
def log_visit():
    """Receives and logs client-side data, including IP address."""
    try:
        data = request.get_json()
        
        data['client_ip'] = get_real_client_ip(request)
        data['serverTimestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data['type'] = 'CLIENT_DATA' 
        
        log_entry = json.dumps(data)
        
        with open(LOG_FILE_PATH, 'a') as f:
            f.write(log_entry + '\n')
            
        print("\n--- VISITOR LOGGED TO FILE ---")
        return jsonify({"status": "success"}), 200
        
    except Exception as e:
        print(f"Error logging visit: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400


@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    """
    Synthesizes speech based on text and a selected narrator WAV, 
    then forces a download.
    """
    if not tts_model:
        return "Error: TTS model not loaded.", 500

    try:
        data = request.get_json()
        text_prompt = data.get('text_prompt')
        narrator_file = data.get('narrator_file') # This is the filename (e.g., 'trump_sample.wav')

        if not text_prompt:
            return "Please enter text to synthesize.", 400

        audio_prompt_path = None
        if narrator_file and narrator_file != 'none':
            # Construct the full filesystem path to the selected WAV file
            audio_prompt_path = os.path.join(SAMPLES_FOLDER, narrator_file)
            if not os.path.exists(audio_prompt_path):
                return f"Error: Narrator file {narrator_file} not found.", 404

        print(f"Generating audio with voice: {narrator_file or 'Default'} for text: '{text_prompt[:50]}...'")

        # --- TTS Generation ---
        # wav is a torch tensor
        wav = tts_model.generate(text_prompt, audio_prompt_path=audio_prompt_path)
        
        # Save the waveform to an in-memory byte buffer
        buffer = io.BytesIO()
        # Use the model's sample rate (tts_model.sr) for saving
        ta.save(buffer, wav.to('cpu'), tts_model.sr, format="wav") 
        buffer.seek(0)

        # Create a unique filename for the download
        download_filename = f"chatterbox_output_{int(time.time())}.wav"

        # Stream the file for automatic download
        return send_file(
            buffer,
            mimetype='audio/wav',
            as_attachment=True,
            download_name=download_filename
        )

    except Exception as e:
        print(f"TTS Generation Error: {e}")
        return f"An error occurred during TTS generation: {e}", 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
