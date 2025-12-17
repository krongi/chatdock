// Global variables to store the audio blob and filename for download
let audioBlobUrl = null;
let audioBlobObj = null;
let audioEvent;
let audioDownloadFilename = 'chatterbox_output.wav'; 
let optHiddenCheck = true
let recHiddenCheck = true
let audioBlobs = []
let options = {'cfgWeightNumInput': 0.5, 'exaggerationNumInput': 0.5, 'temperatureNumInput': 0.8}
let recordStream = null;
let temperatureNumInput
let exaggerationNumInput
let cfgWeightNumInput
const recordBtn = document.getElementById('record-button')
// let cfgCurrent = document.getElementById("cfgWeightNumInput")
// let exgCurrent = document.getElementById("exaggerationNumInput")
// let tmpCurrent = document.getElementById("temperatureNumInput")
const optionButton = document.getElementById('optBtn')
const cfgWeightInput = document.getElementById('cfgWeightNumInput')
const exaggerationInput = document.getElementById('exaggerationNumInput')
const temperatureInput = document.getElementById('temperatureNumInput')



// New function to update the displayed file name and clear select
function updateFileNameDisplay(input) {
    const filenameDisplay = document.getElementById('upload-filename');
    if (input.files.length > 0) {
        filenameDisplay.textContent = `File selected: ${input.files[0].name}`;
    } else {
        filenameDisplay.textContent = 'Or click here to upload a WAV/MP3 file...';
    }
}

function removeAnimations() {
    const recordButton = document.getElementById('record-button')
    const pauseButton = document.getElementById('pause-button')
    const stopButton = document.getElementById('stop-button')
    const buttonList = [recordButton, pauseButton, stopButton]
    for(i=0; i<buttonList.length; i++) {
        buttonList[i].style.animation = "none"
    }
}

function chrisHansen(event) {
    console.log(event)
    // console.log(event)
    console.log("I like rape...")
}

function updateValue(event) {
     document.getElementById(event.target).value
}

function handleChange(event) {
    // return document.getElementById(event.target).value

    console.log("current target: " + options[event.target.id])
    console.log("Event target: " + event.target.value)
    console.log("Event current target: " + event.currentTarget.value)
}

function dataAvailable(event) {
    // audioBlobs.push(event.target.requestData())
    audioEvent = event
    audioBlobObj = audioEvent.data
    const url = window.URL.createObjectURL(audioBlobObj);
    const audioContext = new AudioContext()
    audioContext.createBuffer(numberOfChannels = 1, length = audioBlobObj.size, sampleRate = 44100);
    audioContext.createBufferSource()
    
    const audioPlayer = document.getElementById('audio-player')
    const playerDiv = document.getElementById('player')
    
    audioPlayer.src = url
    playerDiv.hidden = false
    audioBlobUrl = url
}

function recordSetup(){
    navigator.mediaDevices.getUserMedia({audio: true})
        .then(stream => {
            const mediaRecorder = new MediaRecorder(stream)
            mediaRecorder.addEventListener('dataavailable', dataAvailable)
            recordStream = mediaRecorder
            return mediaRecorder
        }
        )
}

function showRecord() {
    const recContainer = document.getElementById('rec-container')
    if (recHiddenCheck == false) {
        recContainer.style.display = "None"
        recHiddenCheck = true
    }
    else {
        recContainer.style.display = "contents"
        recHiddenCheck = false
        removeAnimations()
        return recordSetup()
    }
}

function startRecord(mediaRecorder=recordStream) {
    const recordLabel = document.getElementById('recording-status-label')
    const recordLabelContainer = document.getElementById('status-label-container')
    const recordButton = document.getElementById('record-button')
    const pauseButton = document.getElementById('pause-button')
    const stopButton = document.getElementById('stop-button')
    mediaRecorder.start()
    removeAnimations()
    recordButton.style.animation = "breathe 1s ease-in-out infinite"
    recordButton.disabled = true
    pauseButton.disabled = false
    stopButton.disabled = false
    recordLabelContainer.hidden = false
    recordLabel.textContent = "Recording..."
    recordLabel.hidden = false
    recordLabel.display = "contents"
    
}

function stopRecord(mediaRecorder=recordStream) {
    const recordLabel = document.getElementById('recording-status-label')
    const recordLabelContainer = document.getElementById('status-label-container')
    const stopButton = document.getElementById('stop-button')
    const recordButton = document.getElementById('record-button')
    const pauseButton = document.getElementById('pause-button')
    mediaRecorder.stop()
    removeAnimations()
    stopButton.style.animation = "breathe 1s ease-in-out 4"
    stopButton.disabled = true
    pauseButton.disabled = true
    recordButton.disabled = false
    recordLabelContainer.hidden = true
    recordLabel.display = "None"
    recordLabel.hidden = true
}

function pauseRecord(mediaRecorder=recordStream) {
    const recordLabel = document.getElementById('recording-status-label')
    
    const pauseButton = document.getElementById('pause-button')
    const recordButton = document.getElementById('record-button')
    const stopButton = document.getElementById('stop-button')
    mediaRecorder.pause()
    removeAnimations()
    pauseButton.style.animation = "breathe 1s ease-in-out infinite"
    stopButton.disabled = false
    pauseButton.disabled = false
    recordButton.disabled = true
    recordLabel.hidden = false
    recordLabel.textContent = "Recording paused..."
}

function showOptions(){
    const optContainer = document.getElementById('opt-container')
    if (optHiddenCheck == false) {
        optContainer.style.display = "None"
        optionButton.style.backgroundColor = "red"
        optionButton.textContent = "SHOW ADDITIONAL OPTIONS"
        optHiddenCheck = true
    }
    else {
        optContainer.style.display = "contents"
        optionButton.style.backgroundColor = "green"
        optionButton.textContent = "HIDE ADDITIONAL OPTIONS"
        optHiddenCheck = false
    }
}

function displayCurrentValue(input_element_id, input_value_label_id) {
    let elementValue = document.getElementById(input_element_id).value
    document.getElementById(input_value_label_id).value = elementValue;
}

function generateTTSAudio() {
    // 1. Retrieve values using the correct HTML IDs
    const textPrompt = document.getElementById('text-prompt').value;
    const narratorFileSelect = document.getElementById('narrator-wav').value; 
    // const uploadedFile = document.getElementById('upload-wav').files[0];
    let uploadedFile
    
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
        let cfg = document.getElementById('cfgWeightNumInput')
        let exg = document.getElementById('exaggerationNumInput')
        let tmp = document.getElementById('temperatureNumInput')
        formData.append('narrator-wav', narratorFileSelect); 
        formData.append('cfg', cfg.value)
        formData.append('exaggeration', exg.value)
        formData.append('temp', tmp.value)
    }

    // 3. START: Reset state, show indicator, and disable button
    generateButton.disabled = true;
    indicator.style.display = 'flex';
    audioPlayerContainer.hidden = true;
    audioPlayer.removeAttribute('src'); // Clear previous audio
    
    audioBlobUrl = null; 

    // NOTICE: Do not set Content-Type: application/json when using FormData
    fetch('/generate_tts_audio', {
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

function uploadAudio(audioEvent) {
    const recordLabel = document.getElementById('recording-status-label')
    if (!audioBlobUrl){
        alert("Please generate audio first.")
        return;
    }

    const audioBlob = new Blob(audioEvent, {type: "audio/wav"});
    const formData = new FormData()
    formData.append('audioEvent', audioBlob, 'uploaded_audio.wav')
    const xhr = new XMLHttpRequest();
    xhr.onload = function() {
        if (this.readyState === 4 && this.status === 200) {
            recordLabel.textContent = 'Status: Upload successful! Server response: ' + this.responseText;
        } else {
            recordLabel.textContent = 'Status: Upload failed. Server returned: ' + this.status;
        }
    };
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        return response.blob()
        
    })
}