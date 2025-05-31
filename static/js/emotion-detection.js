
// Webcam setup
const video = document.getElementById('webcam');
const emotionLabel = document.getElementById('detected-emotion-label');
const detectionDetails = document.getElementById('detection-details');
const statusMessage = document.getElementById('status-message');
const errorMessage = document.getElementById('error-message');
const runButton = document.getElementById('run-btn');
const emotionTimeline = document.getElementById('emotion-timeline');

let stream = null;
let isDetecting = true;
let detectionInterval = null;

async function setupWebcam() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        startContinuousDetection();
    } catch (err) {
        console.error('Error accessing webcam:', err);
        showError('Could not access webcam. Please ensure you have granted camera permissions.');
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    statusMessage.style.display = 'none';
}

function showStatus(message) {
    statusMessage.textContent = message;
    statusMessage.style.display = 'block';
    errorMessage.style.display = 'none';
}

function clearMessages() {
    errorMessage.style.display = 'none';
    statusMessage.style.display = 'none';
}

async function captureFrame() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg');
}

async function detectEmotion() {
    if (!isDetecting) return;

    try {
        const imageData = await captureFrame();
        
        const response = await fetch('/api/detect_emotion/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            emotionLabel.textContent = result.emotion.charAt(0).toUpperCase() + result.emotion.slice(1);
            detectionDetails.textContent = `Confidence: ${(result.confidence * 100).toFixed(2)}%`;
            
            // Update emotion timeline
            updateEmotionTimeline();
            
            // Show suggestion if available
            if (result.suggestion) {
                showStatus(result.suggestion);
            } else {
                clearMessages();
            }
        } else {
            showError(result.message);
        }
    } catch (error) {
        console.error('Error detecting emotion:', error);
    }
}

function startContinuousDetection() {
    // Detect emotion every 2 seconds
    detectionInterval = setInterval(detectEmotion, 2000);
}

function stopDetection() {
    isDetecting = false;
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }
}

// Expose start and stop detection functions globally for external control
window.startDetection = function() {
    if (!isDetecting) {
        isDetecting = true;
        startContinuousDetection();
    }
};

window.stopDetection = function() {
    stopDetection();
};

async function updateEmotionTimeline() {
    try {
        const response = await fetch('/api/get_emotion_history/');
        const result = await response.json();
        
        if (result.status === 'success') {
            emotionTimeline.innerHTML = '';
            result.history.forEach(entry => {
                const entryElement = document.createElement('div');
                entryElement.className = 'emotion-history-entry';
                entryElement.innerHTML = `
                    <span class="emotion">${entry.emotion}</span>
                    <span class="confidence">${(entry.confidence * 100).toFixed(2)}%</span>
                    <span class="time">${new Date(entry.timestamp).toLocaleTimeString()}</span>
                `;
                emotionTimeline.appendChild(entryElement);
            });
        }
    } catch (error) {
        console.error('Error updating emotion timeline:', error);
    }
}

// Event listeners
runButton.addEventListener('click', () => {
    stopDetection();
    // After code execution completes, restart detection
    setTimeout(() => {
        isDetecting = true;
        startContinuousDetection();
    }, 5000); // Wait 5 seconds before restarting detection
});

// Add event listener for submit button to stop webcam and detection
const submitButton = document.getElementById('submit-btn');
submitButton.addEventListener('click', () => {
    stopDetection();
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
});

const emotionCallbacks = [];

window.registerEmotionCallback = function(callback) {
    if (typeof callback === 'function') {
        emotionCallbacks.push(callback);
    }
};

async function detectEmotion() {
    if (!isDetecting) return;

    try {
        const imageData = await captureFrame();
        
        const response = await fetch('/api/detect_emotion/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            emotionLabel.textContent = result.emotion.charAt(0).toUpperCase() + result.emotion.slice(1);
            detectionDetails.textContent = `Confidence: ${(result.confidence * 100).toFixed(2)}%`;
            
            // Call registered callbacks with detected emotion
            emotionCallbacks.forEach(cb => cb(result.emotion));
            
            // Update emotion timeline
            updateEmotionTimeline();
            
            // Show suggestion if available
            if (result.suggestion) {
                showStatus(result.suggestion);
            } else {
                clearMessages();
            }
        } else {
            showError(result.message);
        }
    } catch (error) {
        console.error('Error detecting emotion:', error);
    }
}

setupWebcam();
updateEmotionTimeline();
// Webcam setup
const video = document.getElementById('webcam');
const emotionLabel = document.getElementById('detected-emotion-label');
const detectionDetails = document.getElementById('detection-details');
const statusMessage = document.getElementById('status-message');
const errorMessage = document.getElementById('error-message');
const runButton = document.getElementById('run-btn');
const emotionTimeline = document.getElementById('emotion-timeline');

let stream = null;
let isDetecting = true;
let detectionInterval = null;

async function setupWebcam() {
    try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        video.srcObject = stream;
        startContinuousDetection();
    } catch (err) {
        console.error('Error accessing webcam:', err);
        showError('Could not access webcam. Please ensure you have granted camera permissions.');
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    statusMessage.style.display = 'none';
}

function showStatus(message) {
    statusMessage.textContent = message;
    statusMessage.style.display = 'block';
    errorMessage.style.display = 'none';
}

function clearMessages() {
    errorMessage.style.display = 'none';
    statusMessage.style.display = 'none';
}

async function captureFrame() {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    return canvas.toDataURL('image/jpeg');
}

async function detectEmotion() {
    if (!isDetecting) return;

    try {
        const imageData = await captureFrame();
        
        const response = await fetch('/api/detect_emotion/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            emotionLabel.textContent = result.emotion.charAt(0).toUpperCase() + result.emotion.slice(1);
            detectionDetails.textContent = `Confidence: ${(result.confidence * 100).toFixed(2)}%`;
            
            // Update emotion timeline
            updateEmotionTimeline();
            
            // Show suggestion if available
            if (result.suggestion) {
                showStatus(result.suggestion);
            } else {
                clearMessages();
            }
        } else {
            showError(result.message);
        }
    } catch (error) {
        console.error('Error detecting emotion:', error);
    }
}

function startContinuousDetection() {
    // Detect emotion every 2 seconds
    detectionInterval = setInterval(detectEmotion, 2000);
}

function stopDetection() {
    isDetecting = false;
    if (detectionInterval) {
        clearInterval(detectionInterval);
        detectionInterval = null;
    }
}

// Expose start and stop detection functions globally for external control
window.startDetection = function() {
    if (!isDetecting) {
        isDetecting = true;
        startContinuousDetection();
    }
};

window.stopDetection = function() {
    stopDetection();
};

async function updateEmotionTimeline() {
    try {
        const response = await fetch('/api/get_emotion_history/');
        const result = await response.json();
        
        if (result.status === 'success') {
            emotionTimeline.innerHTML = '';
            result.history.forEach(entry => {
                const entryElement = document.createElement('div');
                entryElement.className = 'emotion-history-entry';
                entryElement.innerHTML = `
                    <span class="emotion">${entry.emotion}</span>
                    <span class="confidence">${(entry.confidence * 100).toFixed(2)}%</span>
                    <span class="time">${new Date(entry.timestamp).toLocaleTimeString()}</span>
                `;
                emotionTimeline.appendChild(entryElement);
            });
        }
    } catch (error) {
        console.error('Error updating emotion timeline:', error);
    }
}

// Event listeners
runButton.addEventListener('click', () => {
    stopDetection();
    // After code execution completes, restart detection
    setTimeout(() => {
        isDetecting = true;
        startContinuousDetection();
    }, 5000); // Wait 5 seconds before restarting detection
});

// Add event listener for submit button to stop webcam and detection
const submitButton = document.getElementById('submit-btn');
submitButton.addEventListener('click', () => {
    stopDetection();
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        video.srcObject = null;
    }
});

const emotionCallbacks = [];

window.registerEmotionCallback = function(callback) {
    if (typeof callback === 'function') {
        emotionCallbacks.push(callback);
    }
};

async function detectEmotion() {
    if (!isDetecting) return;

    try {
        const imageData = await captureFrame();
        
        const response = await fetch('/api/detect_emotion/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ image: imageData }),
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            emotionLabel.textContent = result.emotion.charAt(0).toUpperCase() + result.emotion.slice(1);
            detectionDetails.textContent = `Confidence: ${(result.confidence * 100).toFixed(2)}%`;
            
            // Call registered callbacks with detected emotion
            emotionCallbacks.forEach(cb => cb(result.emotion));
            
            // Update emotion timeline
            updateEmotionTimeline();
            
            // Show suggestion if available
            if (result.suggestion) {
                showStatus(result.suggestion);
            } else {
                clearMessages();
            }
        } else {
            showError(result.message);
        }
    } catch (error) {
        console.error('Error detecting emotion:', error);
    }
}

setupWebcam();
updateEmotionTimeline();

