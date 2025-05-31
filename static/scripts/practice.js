
 // Initialize Monaco Editor
 require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs' } });
 require(['vs/editor/editor.main'], function () {
     const editor = monaco.editor.create(document.getElementById('editor'), {
         value: '// Write your code here\n',
         language: 'javascript',
         theme: 'vs',
         automaticLayout: true,
         minimap: {
             enabled: false
         }
     });

     const languageSelect = document.getElementById('language-select');
     languageSelect.addEventListener('change', function () {
         const language = this.value;
         monaco.editor.setModelLanguage(editor.getModel(), language);
     });

     const runButton = document.getElementById('run-btn');
     runButton.addEventListener('click', async function () {
         const code = editor.getValue();
         const language = languageSelect.value;
         const outputContent = document.getElementById('output-content');

         outputContent.textContent = 'Running...';

         try {
             const response = await fetch('/api/execute/', {
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({ code: code, language: language })
             });

             const result = await response.json();

             if (result.status === 'success') {
                 outputContent.textContent = result.output;
             } else {
                 outputContent.textContent = `Error: ${result.message}`;
             }
         } catch (error) {
             outputContent.textContent = `Error: ${error.message}`;
         }
     });
 });

console.log("Initializing emotionCount and related variables globally.");
// === Emotion-based Difficulty Adjustment ===
let emotionCount = { happy: 0, sad: 0 };
let currentDifficulty = 'medium'; // Default level
let emotionDetectionActive = true;
let increaseDifficultyNext = false;

function showDifficultyPrompt(message) {
    const promptDiv = document.getElementById('difficulty-prompt');
    // Remove setting textContent to avoid overwrite
    // promptDiv.textContent = message;
    promptDiv.style.display = 'block';

    console.log("Showing difficulty prompt:", message);

    // Add buttons for user response
    promptDiv.innerHTML = `
        <p>${message}</p>
        <button id="accept-btn">Yes</button>
        <button id="decline-btn">No</button>
    `;

    return new Promise((resolve) => {
        document.getElementById('accept-btn').onclick = () => {
            promptDiv.style.display = 'none';
            resolve(true);
        };
        document.getElementById('decline-btn').onclick = () => {
            promptDiv.style.display = 'none';
            resolve(false);
        };
    });
}

async function changeDifficulty(level) {
    currentDifficulty = level;
    console.log(`Changing difficulty to: ${level}`);

    try {
        const response = await fetch(`/api/get_question?difficulty=${level}`);
        const data = await response.json();

        if (data.status === 'success') {
            // Update UI with the new question
            document.querySelector('.problem-description h2').textContent = data.title;
            document.querySelector('.description-content p').textContent = data.description;
            const difficultySpan = document.querySelector('.difficulty');
            difficultySpan.textContent = level;
            difficultySpan.className = 'difficulty ' + level;
        } else {
            console.error("Failed to load question:", data.message);
        }
    } catch (err) {
        console.error("Failed to load question:", err);
    }
}

async function updateEmotion(emotion) {
    console.log("updateEmotion called with emotion:", emotion);
    if (!emotionDetectionActive) {
        console.log("Emotion detection is inactive, skipping updateEmotion.");
        return;
    }

    // Normalize emotion string to lowercase
    const normalizedEmotion = emotion.toLowerCase();

    // Add detected emotion to emotion history UI
    const emotionTimeline = document.getElementById('emotion-timeline');
    if (emotionTimeline) {
        const emotionEntry = document.createElement('div');
        emotionEntry.className = 'emotion-entry ' + normalizedEmotion;
        emotionEntry.textContent = normalizedEmotion.charAt(0).toUpperCase() + normalizedEmotion.slice(1);
        emotionTimeline.appendChild(emotionEntry);
    }

    if (normalizedEmotion === 'happy') {
        emotionCount.happy++;
        emotionCount.sad = 0;
        console.log("Happy count:", emotionCount.happy);

        if (emotionCount.happy >= 5) {
            // Only set increaseDifficultyNext if current difficulty is hard
            if (currentDifficulty === 'hard') {
                increaseDifficultyNext = true;
                console.log("Set increaseDifficultyNext to true for hard difficulty");
            }
            emotionCount.happy = 0;
        }
    } else if (normalizedEmotion === 'sad') {
        emotionCount.sad++;
        emotionCount.happy = 0;
        console.log("Sad count:", emotionCount.sad);

        if (emotionCount.sad >=3) {
            emotionCount.sad = 0;
            console.log("Sad count exceeded 3, showing prompt");
            // Immediately show prompt and reduce difficulty and shift question
            if (currentDifficulty === 'hard') {
                if (await showDifficultyPrompt("It seems you're struggling. Try a medium difficulty question?")) {
                    await changeDifficulty('medium');
                }
            } else if (currentDifficulty === 'medium') {
                if (await showDifficultyPrompt("Need a break? Let's try something easier.")) {
                    await changeDifficulty('easy');
                }
            } else if (currentDifficulty === 'easy') {
                if (await showDifficultyPrompt("It seems you're struggling. Want to try another easy question?")) {
                    await changeDifficulty('easy');
                }
            }
        }
    }
}

async function onSubmit() {
    console.log("Submit button clicked, stopping emotion detection.");
    emotionDetectionActive = false;

    // Stop webcam stream to turn off camera
    if (video.srcObject) {
        const tracks = video.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
        console.log("Webcam stream stopped.");
    }

    // Save code and check correctness logic here
    // ...

    if (increaseDifficultyNext) {
        increaseDifficultyNext = false;
        if (currentDifficulty === 'easy') {
            await changeDifficulty('medium');
        } else if (currentDifficulty === 'medium') {
            await changeDifficulty('hard');
        } else if (currentDifficulty === 'hard') {
            // Already at highest difficulty, optionally notify user or keep at hard
            console.log("Already at highest difficulty level.");
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('submit-btn').addEventListener('click', onSubmit);
});

const video = document.getElementById('webcam');
const emotionLabel = document.getElementById('detected-emotion-label');
const detectionDetails = document.getElementById('detection-details');
const errorMessage = document.getElementById('error-message');

async function setupWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Webcam access denied:", err);
        errorMessage.style.display = 'block';
        errorMessage.textContent = "Webcam access denied.";
    }
}

function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL('image/jpeg');
}

async function detectEmotion() {
    const imageData = captureImage(); // Assuming this function captures base64 image data

    try {
        const response = await fetch('/api/detect_emotion/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const result = await response.json();
        if (result.status === 'success') {
            emotionLabel.textContent = result.emotion;
            detectionDetails.innerHTML = `Confidence: ${(result.confidence * 100).toFixed(2)}%`;
            updateEmotion(result.emotion);
        } else {
            emotionLabel.textContent = 'No face detected';
            detectionDetails.innerHTML = '';
        }
    } catch (error) {
        console.error("Error detecting emotion:", error);
        errorMessage.style.display = 'block';
        errorMessage.textContent = "Error detecting emotion.";
    }
}

setupWebcam().then(() => {
    setInterval(detectEmotion, 5000);  // Every 5 seconds
});
 // Initialize Monaco Editor
 require.config({ paths: { 'vs': 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.36.1/min/vs' } });
 require(['vs/editor/editor.main'], function () {
     const editor = monaco.editor.create(document.getElementById('editor'), {
         value: '// Write your code here\n',
         language: 'javascript',
         theme: 'vs',
         automaticLayout: true,
         minimap: {
             enabled: false
         }
     });

     const languageSelect = document.getElementById('language-select');
     languageSelect.addEventListener('change', function () {
         const language = this.value;
         monaco.editor.setModelLanguage(editor.getModel(), language);
     });

     const runButton = document.getElementById('run-btn');
     runButton.addEventListener('click', async function () {
         const code = editor.getValue();
         const language = languageSelect.value;
         const outputContent = document.getElementById('output-content');

         outputContent.textContent = 'Running...';

         try {
             const response = await fetch('/api/execute/', {
                 method: 'POST',
                 headers: { 'Content-Type': 'application/json' },
                 body: JSON.stringify({ code: code, language: language })
             });

             const result = await response.json();

             if (result.status === 'success') {
                 outputContent.textContent = result.output;
             } else {
                 outputContent.textContent = `Error: ${result.message}`;
             }
         } catch (error) {
             outputContent.textContent = `Error: ${error.message}`;
         }
     });
 });

console.log("Initializing emotionCount and related variables globally.");
// === Emotion-based Difficulty Adjustment ===
let emotionCount = { happy: 0, sad: 0 };
let currentDifficulty = 'medium'; // Default level
let emotionDetectionActive = true;
let increaseDifficultyNext = false;

function showDifficultyPrompt(message) {
    const promptDiv = document.getElementById('difficulty-prompt');
    // Remove setting textContent to avoid overwrite
    // promptDiv.textContent = message;
    promptDiv.style.display = 'block';

    console.log("Showing difficulty prompt:", message);

    // Add buttons for user response
    promptDiv.innerHTML = `
        <p>${message}</p>
        <button id="accept-btn">Yes</button>
        <button id="decline-btn">No</button>
    `;

    return new Promise((resolve) => {
        document.getElementById('accept-btn').onclick = () => {
            promptDiv.style.display = 'none';
            resolve(true);
        };
        document.getElementById('decline-btn').onclick = () => {
            promptDiv.style.display = 'none';
            resolve(false);
        };
    });
}

async function changeDifficulty(level) {
    currentDifficulty = level;
    console.log(`Changing difficulty to: ${level}`);

    try {
        const response = await fetch(`/api/get_question?difficulty=${level}`);
        const data = await response.json();

        if (data.status === 'success') {
            // Update UI with the new question
            document.querySelector('.problem-description h2').textContent = data.title;
            document.querySelector('.description-content p').textContent = data.description;
            const difficultySpan = document.querySelector('.difficulty');
            difficultySpan.textContent = level;
            difficultySpan.className = 'difficulty ' + level;
        } else {
            console.error("Failed to load question:", data.message);
        }
    } catch (err) {
        console.error("Failed to load question:", err);
    }
}

async function updateEmotion(emotion) {
    console.log("updateEmotion called with emotion:", emotion);
    if (!emotionDetectionActive) {
        console.log("Emotion detection is inactive, skipping updateEmotion.");
        return;
    }

    // Normalize emotion string to lowercase
    const normalizedEmotion = emotion.toLowerCase();

    // Add detected emotion to emotion history UI
    const emotionTimeline = document.getElementById('emotion-timeline');
    if (emotionTimeline) {
        const emotionEntry = document.createElement('div');
        emotionEntry.className = 'emotion-entry ' + normalizedEmotion;
        emotionEntry.textContent = normalizedEmotion.charAt(0).toUpperCase() + normalizedEmotion.slice(1);
        emotionTimeline.appendChild(emotionEntry);
    }

    if (normalizedEmotion === 'happy') {
        emotionCount.happy++;
        emotionCount.sad = 0;
        console.log("Happy count:", emotionCount.happy);

        if (emotionCount.happy >= 5) {
            // Only set increaseDifficultyNext if current difficulty is hard
            if (currentDifficulty === 'hard') {
                increaseDifficultyNext = true;
                console.log("Set increaseDifficultyNext to true for hard difficulty");
            }
            emotionCount.happy = 0;
        }
    } else if (normalizedEmotion === 'sad') {
        emotionCount.sad++;
        emotionCount.happy = 0;
        console.log("Sad count:", emotionCount.sad);

        if (emotionCount.sad >=3) {
            emotionCount.sad = 0;
            console.log("Sad count exceeded 3, showing prompt");
            // Immediately show prompt and reduce difficulty and shift question
            if (currentDifficulty === 'hard') {
                if (await showDifficultyPrompt("It seems you're struggling. Try a medium difficulty question?")) {
                    await changeDifficulty('medium');
                }
            } else if (currentDifficulty === 'medium') {
                if (await showDifficultyPrompt("Need a break? Let's try something easier.")) {
                    await changeDifficulty('easy');
                }
            } else if (currentDifficulty === 'easy') {
                if (await showDifficultyPrompt("It seems you're struggling. Want to try another easy question?")) {
                    await changeDifficulty('easy');
                }
            }
        }
    }
}

async function onSubmit() {
    console.log("Submit button clicked, stopping emotion detection.");
    emotionDetectionActive = false;

    // Stop webcam stream to turn off camera
    if (video.srcObject) {
        const tracks = video.srcObject.getTracks();
        tracks.forEach(track => track.stop());
        video.srcObject = null;
        console.log("Webcam stream stopped.");
    }

    // Save code and check correctness logic here
    // ...

    if (increaseDifficultyNext) {
        increaseDifficultyNext = false;
        if (currentDifficulty === 'easy') {
            await changeDifficulty('medium');
        } else if (currentDifficulty === 'medium') {
            await changeDifficulty('hard');
        } else if (currentDifficulty === 'hard') {
            // Already at highest difficulty, optionally notify user or keep at hard
            console.log("Already at highest difficulty level.");
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('submit-btn').addEventListener('click', onSubmit);
});

const video = document.getElementById('webcam');
const emotionLabel = document.getElementById('detected-emotion-label');
const detectionDetails = document.getElementById('detection-details');
const errorMessage = document.getElementById('error-message');

async function setupWebcam() {
    try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
    } catch (err) {
        console.error("Webcam access denied:", err);
        errorMessage.style.display = 'block';
        errorMessage.textContent = "Webcam access denied.";
    }
}

function captureImage() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    return canvas.toDataURL('image/jpeg');
}

async function detectEmotion() {
    const imageData = captureImage(); // Assuming this function captures base64 image data

    try {
        const response = await fetch('/api/detect_emotion/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ image: imageData })
        });

        const result = await response.json();
        if (result.status === 'success') {
            emotionLabel.textContent = result.emotion;
            detectionDetails.innerHTML = `Confidence: ${(result.confidence * 100).toFixed(2)}%`;
            updateEmotion(result.emotion);
        } else {
            emotionLabel.textContent = 'No face detected';
            detectionDetails.innerHTML = '';
        }
    } catch (error) {
        console.error("Error detecting emotion:", error);
        errorMessage.style.display = 'block';
        errorMessage.textContent = "Error detecting emotion.";
    }
}

setupWebcam().then(() => {
    setInterval(detectEmotion, 5000);  // Every 5 seconds
});
