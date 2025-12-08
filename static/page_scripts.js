function generateAudio() {
    let textPrompt = document.getElementById('text-prompt').value;
    let narratorFile = document.getElementById('narrator-wav').value;

    if (!textPrompt) {
        alert("Please enter some text to generate audio.");
        return;
    }

    // You might want to disable the button here to prevent multiple clicks
    let generateButton = document.querySelector('.btn-generate');
    generateButton.disabled = true;

    fetch('/generate_audio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            text_prompt: textPrompt,
            narrator_file: narratorFile
        })
    })
    .then(response => {
        // If the server returns a successful stream, prompt for download
        generateButton.disabled = false;
        if (response.ok && response.headers.get('Content-Type') === 'audio/wav') {
            // This triggers the automatic download
            return response.blob();
        } else if (response.ok) {
            // Handle JSON error response if generation fails server-side
            return response.json().then(data => { throw new Error(data.message); });
        } else {
            throw new Error('Server returned an error.');
        }
    })
    .then(blob => {
        // Create a link element, set its attributes, and simulate a click to download
        let url = window.URL.createObjectURL(blob);
        let a = document.createElement('a');
        a.style.display = 'none';
        a.href = url;
        // The server provides the download_name via the Content-Disposition header, 
        // but we ensure it works even if that fails.
        a.download = 'chatterbox_output.wav'; 
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
    })
    .catch(error => {
        alert("Audio generation failed: " + error.message);
    })
    // .finally(() => {
    //     // Re-enable the button
    //     generateButton.disabled = false;
    // });
}

function clearText() {
    document.getElementById('text-prompt').value = '';
}
