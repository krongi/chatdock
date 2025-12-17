import os
import io
import time
import json
import tempfile
from flask import Flask, render_template, request, send_file, jsonify, make_response
from datetime import datetime
import torchaudio as ta
import torch
from chatterbox.tts import ChatterboxTTS

# --- Configuration ---
SAMPLES_FOLDER = 'static/samples'
LOG_FILE_PATH = 'visitor_logs.txt'

LONG_STRING = """Earlier in the year on YouTube, Yaniv Hoffman and Occupy The Web haved discussed research showing how Wi-Fi signals can be used to detect and track people through walls. The idea is simple from an RF point of view. Wi-Fi is just radio, and when those signals pass through a room they reflect and scatter off walls, furniture, and human bodies. By analyzing these reflections, it is possible to infer movement and even rough human outlines without placing any hardware inside the room.

Using low-cost SDRs, a standard PC, an NVIDIA GPU, and open-source AI tools like DensePose, researchers can reconstruct basic 3D human shapes in real time. In some cases, the system does not even need to transmit its own signal. It can passively analyze reflections from an existing Wi-Fi router already operating in the home.

The speakers note that this raises obvious privacy concerns. While there are some benign uses like motion-based home security or monitoring breathing in elderly care, the same techniques could be misused. Countermeasures are limited, as Wi-Fi uses spread spectrum techniques that make jamming difficult. """

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
    tts_model = ChatterboxTTS.from_pretrained(device=device)
    print("ChatterboxTTS model loaded successfully.")
except Exception as e:
    print(f"Error loading TTS model: {e}. Please check your Chatterbox installation.")
    tts_model = None

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

def breakdown_prompt(text_prompt_string):
    text_prompt_string_list = text_prompt_string.splitlines()
    secondary_string_list = []
    for item in text_prompt_string_list:
        if item != '':
            secondary_string_list.append(item)
    for item in secondary_string_list:
        item.strip()
    third_string_list = []
    for item in secondary_string_list:
        for chunk in item.split('.'):
            third_string_list.append(chunk)
    final_string_list = []
    for item in third_string_list:
        for chunk in item.split(','):
            final_string_list.append(chunk)
    return final_string_list

# --- Flask Routes ---

@app.route("/upload", methods=['POST'])
def upload():
    try:
        data = request.get_json()
        print(data)
        with open('sample_voice.wav', 'w') as file:
            file.write(data)
    except:
        print("nope")


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


@app.route('/generate_tts_audio', methods=['POST'])
def generate_tts_audio():
    if not tts_model:
        return jsonify({'error': 'TTS model not loaded.'}), 500

    # CRITICAL FIX: Retrieve data using keys matching the HTML IDs from the frontend
    text_prompt = request.form.get('text-prompt') 
    prompt_list = breakdown_prompt(text_prompt)
    narrator_file_selection = request.form.get('narrator-wav') 
    uploaded_file = request.files.get('upload-wav') 
    cfg = request.form.get('cfg')
    exaggeration = request.form.get('exaggeration')
    temperature = request.form.get('temp')

    temp_file_path = None
    audio_prompt_path = None

    if not text_prompt:
        return jsonify({'error': 'No text prompt provided.'}), 400

    try:
        if uploaded_file and uploaded_file.filename != '':
            # --- UPLOAD PATH ---
            print(f"Processing uploaded file: {uploaded_file.filename}")
            
            suffix = os.path.splitext(uploaded_file.filename)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                uploaded_file.save(tmp.name)
                temp_file_path = tmp.name
                audio_prompt_path = temp_file_path
            
        elif narrator_file_selection and narrator_file_selection != 'none':
            # --- SELECT PATH ---
            print(f"Processing sample file: {narrator_file_selection}")
            
            audio_prompt_path = os.path.join(app.root_path, SAMPLES_FOLDER, narrator_file_selection)
            if not os.path.exists(audio_prompt_path):
                 return jsonify({'error': f'Sample file {narrator_file_selection} not found on server.'}), 404
        
        else:
            return jsonify({'error': 'No narrator source provided.'}), 400

        # --- TTS GENERATION ---
        print(f"Generating audio for text: '{text_prompt[:50]}...' using voice: {audio_prompt_path or 'Default'}")
        
        # Call the actual model function
        buffer = io.BytesIO()
        wavs = []
        for chunk in prompt_list:
            wavs.append(tts_model.generate(chunk, cfg_weight=float(cfg), temperature=float(temperature), exaggeration=float(exaggeration), audio_prompt_path=audio_prompt_path))
        for wav in wavs:
            ta.save(buffer, wav.to('cpu'), tts_model.sr, format="wav") 
        buffer.seek(0)
        
        # --- RESPONSE SETUP ---
        nar_name = narrator_file_selection.split('.')[0]
        download_filename = f"{nar_name}_cfg{cfg}_exag{exaggeration}_temp{temperature}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav"
        
        response = make_response(buffer.getvalue())
        response.headers.set('Content-Type', 'audio/wav')
        response.headers.set('Content-Disposition', 'inline', filename=download_filename)
        
        return response
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error during audio generation: {e}")
        return jsonify({'error': f'An error occurred during TTS: {str(e)}'}), 500
        
    finally:
        # Clean up the temporary file, ensuring it's deleted
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                print(f"Successfully deleted temporary file: {temp_file_path}")
            except Exception as e:
                print(f"Warning: Could not delete temporary file {temp_file_path}. Error: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)