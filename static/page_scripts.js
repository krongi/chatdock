// Global variables to store the audio blob and filename for download
let audioBlobUrl = null;
let audioDownloadFilename = 'chatterbox_output.wav'; 

// New function to update the displayed file name and clear select
function updateFileNameDisplay(input) {
    const filenameDisplay = document.getElementById('upload-filename');
    if (input.files.length > 0) {
        filenameDisplay.textContent = `File selected: ${input.files[0].name}`;
    } else {
        filenameDisplay.textContent = 'Or click here to upload a WAV/MP3 file...';
    }
}

function generateAudio() {
    // 1. Retrieve values using the correct HTML IDs
    const textPrompt = document.getElementById('text-prompt').value;
    const narratorFileSelect = document.getElementById('narrator-wav').value; 
    const uploadedFile = document.getElementById('upload-wav').files[0];
    
    // --- Target specific DOM Elements ---
    const generateButton = document.querySelector('.btn-generate');
    const indicator = document.getElementById('loading-indicator');
    const audioPlayerContainer = document.getElementById('player');
    const audioPlayer = document.getElementById('audio-player');

    if (!textPrompt) {
        alert("Please enter some text to generate audio.");
        return;
    }

    if (narratorFileSelect === 'none' && !uploadedFile) {
        alert("Please select a sample voice or upload a narrator voice file.");
        return;
    }
    
    // 2. Use FormData for file submission
    const formData = new FormData();
    
    // CRITICAL FIX: Use the HTML ID name as the FormData key
    formData.append('text-prompt', textPrompt); 

    if (uploadedFile) {
        // Use 'upload-wav' key for the file
        formData.append('upload-wav', uploadedFile); 
    } else {
        // Use 'narrator-wav' key for the selected filename string
        formData.append('narrator-wav', narratorFileSelect); 
    }

    // 3. START: Reset state, show indicator, and disable button
    generateButton.disabled = true;
    indicator.style.display = 'flex';
    audioPlayerContainer.hidden = true;
    audioPlayer.removeAttribute('src'); // Clear previous audio
    
    audioBlobUrl = null; 

    // NOTICE: Do not set Content-Type: application/json when using FormData
    fetch('/generate_audio', {
        method: 'POST',
        body: formData // Send the FormData object
    })
    .then(response => {
        if (!response.ok) {
            // Read error response text/JSON for better message
            return response.text().then(text => { 
                try {
                    const errorJson = JSON.parse(text);
                    throw new Error(errorJson.error || 'Server returned an unknown error.');
                } catch {
                    throw new Error(text || 'Server returned an error.');
                }
            });
        }
        
        // Extract filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        if (contentDisposition) {
            const match = contentDisposition.match(/filename=["']?([^"']+)["']?/i);
            if (match && match[1]) {
                audioDownloadFilename = match[1];
            }
        }
        
        return response.blob();
    })
    .then(blob => {
        // SUCCESS: Set the audio player source
        const url = window.URL.createObjectURL(blob);
        audioBlobUrl = url; // Store for download function
        
        audioPlayer.src = url;
        audioPlayerContainer.hidden = false;
        
    })
    .catch(error => {
        alert("Audio generation failed: " + error.message);
    })
    .finally(() => {
        // END: Hide indicator and re-enable button
        indicator.style.display = 'none';
        generateButton.disabled = false;
    });
}

function clearText() {
    document.getElementById('text-prompt').value = '';
}

function downloadAudio() {
    if (!audioBlobUrl) {
        alert("Please generate audio first.");
        return;
    }
    
    // Create an anchor tag to simulate the download
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = audioBlobUrl;
    
    // Use the filename captured from the server response header
    a.download = audioDownloadFilename; 
    
    document.body.appendChild(a);
    a.click();
    
    // Clean up the temporary anchor tag
    document.body.removeChild(a);
}